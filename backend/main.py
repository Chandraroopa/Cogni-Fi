from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocketDisconnect

import asyncio
import os
import threading

from backend.capture.adapter import TSharkCapture
from backend.capture.feature_window import (
    CausalWindowManager,
    FeatureExtractor,
)
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
        "service": "Cognifi Wi-Fi Security Backend",
    }


def collect_packets(interface, packet_queue, stop_event, loop):
    """Capture packets on a background thread and enqueue them safely."""
    capture = TSharkCapture(interface=interface)

    def enqueue_packet(packet):
        if stop_event.is_set():
            return

        try:
            packet_queue.put_nowait(packet)
        except asyncio.QueueFull:
            print("[TShark] Packet queue full; dropping packet.")

    try:
        print(f"[TShark] Capture worker started on interface {interface}.")

        for packet in capture.packets():
            if stop_event.is_set():
                break

            try:
                loop.call_soon_threadsafe(enqueue_packet, packet)
            except RuntimeError:
                # Event loop has already closed.
                break

    except Exception as exc:
        if not stop_event.is_set():
            print(f"[TShark] Capture error: {exc}")

    finally:
        print("[TShark] Capture worker stopped.")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("[WS] Client connected.")

    interface = os.getenv("COGNIFI_INTERFACE", "5")
    loop = asyncio.get_running_loop()

    extractor = FeatureExtractor(window_size=1.0)
    window_manager = CausalWindowManager(window_size=1.0)
    detector = LiveRiskDetector()

    packet_queue = asyncio.Queue(maxsize=2000)
    stop_event = threading.Event()

    capture_task = asyncio.create_task(
        asyncio.to_thread(
            collect_packets,
            interface,
            packet_queue,
            stop_event,
            loop,
        )
    )

    last_status_time = loop.time()

    async def process_windows(windows):
        """Extract features and send risk updates for completed windows."""
        for window in windows:
            window_packets = window["packets"]

            if not window_packets:
                continue

            features = extractor.extract_window_features(
                window_packets,
                duration=1.0,
            )
            risk = detector.analyze(features)

            await websocket.send_json({
                "type": "risk_update",
                "features": features,
                "risk": risk,
            })

            print(
                f"[RISK] Window {window.get('window_id', '?')} "
                f"| Packets: {len(window_packets)} "
                f"| {risk.get('risk_level', 'Unknown')} "
                f"| Score: {risk.get('risk_score', 'N/A')}"
            )

    try:
        print(f"[TShark] Starting capture on interface {interface}...")

        while True:
            try:
                packet = await asyncio.wait_for(
                    packet_queue.get(),
                    timeout=1.0,
                )

            except asyncio.TimeoutError:
                now = loop.time()

                if now - last_status_time >= 5.0:
                    await websocket.send_json({
                        "type": "status",
                        "message": "Waiting for live packets...",
                        "interface": interface,
                    })
                    last_status_time = now

                if capture_task.done():
                    worker_error = capture_task.exception()

                    if worker_error is not None:
                        raise RuntimeError(
                            f"Capture worker failed: {worker_error}"
                        )

                    print("[TShark] Capture worker exited.")

                    await websocket.send_json({
                        "type": "error",
                        "error": (
                            "The packet capture worker stopped. "
                            "Check the backend terminal for capture errors."
                        ),
                    })
                    break

                continue

            print(
                f"[PACKET] "
                f"length={packet.get('length', packet.get('frame.len'))} "
                f"| source={packet.get('source')} "
                f"| destination={packet.get('destination')}"
            )

            completed_windows = window_manager.add_packet(packet)
            await process_windows(completed_windows)

    except WebSocketDisconnect:
        print("[WS] Client disconnected.")

    except Exception as exc:
        print(f"[WS] Error: {exc}")

        try:
            await websocket.send_json({
                "type": "error",
                "error": str(exc),
            })
        except Exception:
            pass

    finally:
        stop_event.set()

        # Flush the final partial window without inventing packets.
        try:
            await process_windows(window_manager.flush())
        except Exception as exc:
            print(f"[WS] Final window processing error: {exc}")

        # Allow the capture worker time to finish.
        try:
            await asyncio.wait_for(
                asyncio.shield(capture_task),
                timeout=2.0,
            )
        except asyncio.TimeoutError:
            print(
                "[TShark] Worker is still stopping. "
                "The capture iterator may be blocked waiting for packets."
            )
        except Exception as exc:
            print(f"[TShark] Worker shutdown error: {exc}")

        print("[WS] Connection cleanup complete.")