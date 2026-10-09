import asyncio
import json
import websockets


async def test():
    uri = "ws://127.0.0.1:8001/ws"

    print("Connecting to Cognifi backend...")

    async with websockets.connect(uri) as websocket:
        print("Connected!")
        print("Waiting for live packets...\n")

        for i in range(10):
            raw_data = await websocket.recv()

            # Convert WebSocket JSON string into Python dictionary
            data = json.loads(raw_data)

            print(f"Risk Update {i + 1}:")
            print(json.dumps(data, indent=2))
            print("-" * 60)


asyncio.run(test())