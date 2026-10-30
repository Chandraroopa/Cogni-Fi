
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocketDisconnect, WebSocketState

import asyncio
import os
import threading
import re
import subprocess
from datetime import datetime, timezone

from backend.capture.adapter import TSharkCapture
from backend.capture.feature_window import (
    CausalWindowManager,
    FeatureExtractor,
)
from backend.ml_service import ml_service
from backend.risk_engine import RiskEngine


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


def collect_packets(interface, packet_queue, stop_event, loop, capture):
    """Read packets in a background thread and enqueue them safely."""

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
                break

    except Exception as exc:
        if not stop_event.is_set():
            print(f"[TShark] Capture error: {exc}")

    finally:
        stop_event.set()

        try:
            capture.stop()
        except Exception as exc:
            print(f"[TShark] Capture stop error: {exc}")

        print("[TShark] Capture worker stopped.")


def get_windows_wifi_signal():
    """Read Windows Wi-Fi signal percentage and optional RSSI."""

    if os.name != "nt":
        return {
            "available": False,
            "error": "Windows Wi-Fi telemetry is only available on Windows.",
        }

    try:
        result = subprocess.run(
            ["netsh", "wlan", "show", "interfaces"],
            capture_output=True,
            text=True,
            timeout=5,
            check=True,
            encoding="utf-8",
            errors="replace",
        )

        output = result.stdout

        signal_match = re.search(
            r"^\s*Signal\s*:\s*(\d+)\s*%",
            output,
            re.MULTILINE | re.IGNORECASE,
        )

        rssi_match = re.search(
            r"^\s*Rssi\s*:\s*(-?\d+)",
            output,
            re.MULTILINE | re.IGNORECASE,
        )

        if not signal_match and not rssi_match:
            return {
                "available": False,
                "error": "Windows did not report Wi-Fi signal values.",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        return {
            "available": True,
            "source": "windows_wifi",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "signal_percent": (
                int(signal_match.group(1)) if signal_match else None
            ),
            "rssi_dbm": (
                int(rssi_match.group(1)) if rssi_match else None
            ),
        }

    except (subprocess.SubprocessError, OSError) as exc:
        return {
            "available": False,
            "error": str(exc),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


def get_windows_wifi_security():
    """
    Read the authentication type of the connected Windows Wi-Fi interface.

    Returns None when authentication information is unavailable.
    """

    if os.name != "nt":
        return None

    try:
        result = subprocess.run(
            ["netsh", "wlan", "show", "interfaces"],
            capture_output=True,
            text=True,
            timeout=5,
            check=True,
            encoding="utf-8",
            errors="replace",
        )

        output = result.stdout

        interface_sections = re.split(
            r"(?=^\s*Name\s*:)",
            output,
            flags=re.MULTILINE | re.IGNORECASE,
        )

        for section in interface_sections:
            state_match = re.search(
                r"^\s*State\s*:\s*(.+?)\s*$",
                section,
                re.MULTILINE | re.IGNORECASE,
            )

            if not state_match:
                continue

            if state_match.group(1).strip().lower() != "connected":
                continue

            authentication_match = re.search(
                r"^\s*Authentication\s*:\s*(.+?)\s*$",
                section,
                re.MULTILINE | re.IGNORECASE,
            )

            if authentication_match:
                authentication = authentication_match.group(1).strip()

                print(
                    "[Wi-Fi Security] Connected authentication: "
                    f"{authentication}"
                )

                return authentication

        print(
            "[Wi-Fi Security] No connected interface authentication found."
        )
        return None

    except (subprocess.SubprocessError, OSError) as exc:
        print(f"[Wi-Fi Security] Could not read authentication: {exc}")
        return None


@app.get("/wifi-signal")
def wifi_signal():
    return get_windows_wifi_signal()


@app.get("/wifi-security")
def wifi_security():
    """Return connected Windows Wi-Fi authentication information."""

    authentication = get_windows_wifi_security()

    return {
        "available": authentication is not None,
        "authentication": authentication,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("[WS] Client connected.")

    interface = os.getenv("COGNIFI_INTERFACE", "5")
    loop = asyncio.get_running_loop()

    extractor = FeatureExtractor(window_size=1.0)
    window_manager = CausalWindowManager(window_size=1.0)
    risk_engine = RiskEngine()

    wifi_security = get_windows_wifi_security()

    if wifi_security:
        print(
            f"[Wi-Fi Security] Risk assessment context: {wifi_security}"
        )
    else:
        print(
            "[Wi-Fi Security] Authentication unavailable; "
            "static risk evidence will remain unavailable."
        )

    packet_queue = asyncio.Queue(maxsize=2000)
    stop_event = threading.Event()
    capture = TSharkCapture(interface=interface)

    def websocket_is_connected():
        return (
            websocket.client_state == WebSocketState.CONNECTED
            and websocket.application_state == WebSocketState.CONNECTED
        )

    async def send_json_if_connected(payload):
        if not websocket_is_connected():
            return False

        try:
            await websocket.send_json(payload)
            return True

        except (WebSocketDisconnect, RuntimeError, OSError) as exc:
            print(f"[WS] Message not sent; connection is closing: {exc}")
            return False

    capture_task = asyncio.create_task(
        asyncio.to_thread(
            collect_packets,
            interface,
            packet_queue,
            stop_event,
            loop,
            capture,
        )
    )

    last_status_time = loop.time()

    async def process_windows(windows):
        """Extract features, run inference, and send risk updates."""

        for window in windows:
            if not websocket_is_connected():
                return

            window_packets = window["packets"]

            if not window_packets:
                continue

            features = extractor.extract_window_features(
                window_packets,
                duration=1.0,
            )

            # The ML service receives the original frozen 30 features.
            ml_result = ml_service.analyze(features)

            # Availability metadata is separate from the model vector.
            # A value is considered available only when the extractor
            # explicitly marks its measurement as available.
            behavioral_availability = {
                "wifi_retry_available": (
                    features.get("wifi_retry_available") is True
                ),
                "wifi_management_frames_available": (
                    features.get("wifi_management_frames_available") is True
                ),
                "rst_rate": (
                    features.get("tcp_rst_available") is True
                ),
                "retransmission_rate": (
                    features.get("tcp_retransmission_available") is True
                ),
                "dns_latency_mean": (
                    features.get("dns_latency_available") is True
                ),
            }

            risk = risk_engine.analyze(
                mode="live",
                ml_result=ml_result,
                behavioral_features=features,
                security=wifi_security,
                behavioral_availability=behavioral_availability,
            )

            sent = await send_json_if_connected({
                "type": "risk_update",
                "features": features,
                "ml": ml_result,
                "risk": risk,
            })

            print(
                f"[RISK] Window {window.get('window_id', '?')} "
                f"| Packets: {len(window_packets)} "
                f"| Status: {risk.get('status', 'Unknown')} "
                f"| Assessment: {risk.get('assessment', 'Unknown')} "
                f"| Score: {risk.get('risk_score', 'N/A')} "
                f"| Factors: {risk.get('factors', {})} "
                f"| Predicted class: "
                f"{ml_result.get('predicted_class', 'Unknown')}"
            )

            if not sent:
                return

    try:
        print(f"[TShark] Starting capture on interface {interface}...")

        while websocket_is_connected():
            try:
                packet = await asyncio.wait_for(
                    packet_queue.get(),
                    timeout=1.0,
                )

            except asyncio.TimeoutError:
                now = loop.time()

                if now - last_status_time >= 5.0:
                    sent = await send_json_if_connected({
                        "type": "status",
                        "message": "Waiting for live packets...",
                        "interface": interface,
                    })

                    last_status_time = now

                    if not sent:
                        break

                if capture_task.done():
                    if capture_task.cancelled():
                        print("[TShark] Capture task was cancelled.")
                    else:
                        worker_error = capture_task.exception()

                        if worker_error is not None:
                            print(
                                f"[TShark] Worker task error: {worker_error}"
                            )

                    print("[TShark] Capture worker exited.")

                    await send_json_if_connected({
                        "type": "error",
                        "error": (
                            "The packet capture worker stopped. "
                            "Check the backend terminal for capture errors."
                        ),
                    })

                    break

                continue

            if not websocket_is_connected():
                break

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

    except asyncio.CancelledError:
        print("[WS] Handler cancelled.")
        raise

    except Exception as exc:
        print(f"[WS] Error: {exc}")

        await send_json_if_connected({
            "type": "error",
            "error": str(exc),
        })

    finally:
        print("[WS] Starting connection cleanup.")

        stop_event.set()

        try:
            capture.stop()
        except Exception as exc:
            print(f"[TShark] Stop request error: {exc}")

        if websocket_is_connected():
            try:
                await process_windows(window_manager.flush())
            except Exception as exc:
                print(f"[WS] Final window processing error: {exc}")

        try:
            await asyncio.wait_for(
                asyncio.shield(capture_task),
                timeout=5.0,
            )

        except asyncio.TimeoutError:
            print(
                "[TShark] Worker did not exit within five seconds. "
                "Check subprocess cleanup in TSharkCapture."
            )

        except asyncio.CancelledError:
            print("[TShark] Capture task was cancelled.")

        except Exception as exc:
            print(f"[TShark] Worker shutdown error: {exc}")

        print("[WS] Connection cleanup complete.")
