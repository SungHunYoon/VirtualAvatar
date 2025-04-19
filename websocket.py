import asyncio
import websockets

clients = set()

async def ws_handler(websocket):
    clients.add(websocket)
    try:
        async for _ in websocket:
            pass
    finally:
        clients.remove(websocket)

async def start_ws_server():
    return await websockets.serve(ws_handler, "localhost", 8765)

async def send_mouth_signal(signal):
    print(f"📤 send_mouth_signal: {signal}")  # ✅ 확인용 출력
    if clients:
        await asyncio.gather(*[client.send(signal) for client in clients])
