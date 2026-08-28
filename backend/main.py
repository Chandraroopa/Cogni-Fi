from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json

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


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    # Interface 4 = laptop's Wi-Fi adapter
    # connected to the Android mobile hotspot.
    interface = "4"

    command = [
        "tshark",
        "-i", interface,
        "-T", "ek",
        "-l",
    ]

    process = None

    try:
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        while True:
            line = await process.stdout.readline()

            if not line:
                break

            try:
                data = json.loads(line.decode("utf-8"))

                await websocket.send_json(data)

            except json.JSONDecodeError:
                continue

    except Exception as e:
        await websocket.send_json({
            "error": str(e)
        })

    finally:
        if process:
            process.terminate()