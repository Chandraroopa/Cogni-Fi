from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocketDisconnect

import asyncio
import json


app = FastAPI(title="Cognifi Wi-Fi Security Backend")


# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Health Check
# --------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "online",
        "service": "Cognifi Wi-Fi Security Backend"
    }


# --------------------------------------------------
# WebSocket Live Packet Capture
# --------------------------------------------------

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    await websocket.accept()

    print("[WS] Client connected.")

    # Interface 5 = Wi-Fi adapter
    interface = "5"

    command = [
        "tshark",
        "-i", interface,
        "-T", "ek",
        "-l",
    ]

    process = None

    try:
        # Start TShark
        print(f"[TShark] Starting capture on interface {interface}...")

        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        print("[TShark] Capture started.")

        # Read TShark output
        while True:

            line = await process.stdout.readline()

            if not line:
                print("[TShark] Capture process ended.")
                break

            try:
                data = json.loads(line.decode("utf-8"))

                # Ignore TShark index/metadata lines
                if "index" in data:
                    continue

                await websocket.send_json(data)

            except json.JSONDecodeError:
                continue

            except WebSocketDisconnect:
                print("[WS] Client disconnected.")
                break

    except WebSocketDisconnect:
        print("[WS] Client disconnected.")

    except Exception as e:
        print(f"[WS] Error: {e}")

        # Do not attempt to send if the connection
        # has already been closed.
        try:
            await websocket.send_json({
                "error": str(e)
            })
        except Exception:
            pass

    finally:
        # Stop TShark
        if process is not None:
            try:
                process.terminate()
                await process.wait()
            except Exception:
                pass

        print("[WS] Connection closed.")