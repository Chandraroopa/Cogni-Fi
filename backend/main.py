from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocketDisconnect

import asyncio
import os

from backend.capture.adapter import TSharkCapture
from backend.capture.feature_window import FeatureExtractor
from backend.capture.live_detector import LiveRiskDetector


app = FastAPI(title="Cognifi Wi-Fi Security Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {
        "status": "online",
        "service": "Cognifi Wi-Fi Security Backend"
    }


def collect_packets(interface, packet_queue, stop_event):
    """
    Run blocking TShark capture outside the FastAPI event loop.
    """
    capture = TSharkCapture(interface=interface)

    try:
        for packet in capture.packets():

            if stop_event.is_set():
                break

            packet_queue.put_nowait(packet)

    except Exception as e:
        print(f"[TShark] Capture error: {e}")

    finally:
        print("[TShark] Capture stopped.")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    print("[WS] Client connected.")

    interface = os.getenv("COGNIFI_INTERFACE", "5")

    extractor = FeatureExtractor(window_size=1.0)
    detector = LiveRiskDetector()

    packet_queue = asyncio.Queue()
    stop_event = asyncio.Event()

    capture_task = asyncio.create_task(
        asyncio.to_thread(
            collect_packets,
            interface,
            packet_queue,
            stop_event
        )
    )

    packets = []

    try:
        print(f"[TShark] Starting capture on interface {interface}...")

        while True:

            # Wait for a packet without blocking FastAPI.
            packet = await asyncio.wait_for(
                packet_queue.get(),
                timeout=5.0
            )

            packets.append(packet)

            print(
                f"[PACKET] {len(packets)} | "
                f"length={packet.get('length')} | "
                f"source={packet.get('source')} | "
                f"destination={packet.get('destination')}"
            )

            # Analyze every 10 packets.
            if len(packets) >= 10:

                features = extractor.extract_window_features(packets)

                risk = detector.analyze(features)

                result = {
                    "type": "risk_update",
                    "features": features,
                    "risk": risk
                }

                await websocket.send_json(result)

                print(
                    f"[RISK] {risk['risk_level']} "
                    f"| Score: {risk['risk_score']}"
                )

                packets.clear()

    except asyncio.TimeoutError:
        print("[WS] No packets received for 5 seconds.")

        try:
            await websocket.send_json({
                "type": "status",
                "message": "Waiting for live packets..."
            })
        except Exception:
            pass

    except WebSocketDisconnect:
        print("[WS] Client disconnected.")

    except Exception as e:
        print(f"[WS] Error: {e}")

        try:
            await websocket.send_json({
                "type": "error",
                "error": str(e)
            })
        except Exception:
            pass

    finally:
        stop_event.set()

        if not capture_task.done():
            capture_task.cancel()

        print("[WS] Connection closed.")