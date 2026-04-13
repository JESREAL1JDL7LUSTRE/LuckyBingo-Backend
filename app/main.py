from fastapi import FastAPI
from fastapi import WebSocket, WebSocketDisconnect

from app.api.routes.player import router as player_router
from app.api.routes.room import router as room_router
from app.state.store import store
from app.websockets.connection_manager import manager

app = FastAPI()

app.include_router(room_router)
app.include_router(player_router)

@app.get("/")
def read_root():
    return {"message": "LuckyBingo backend is running"}


@app.websocket("/ws/{room_code}")
async def room_websocket(websocket: WebSocket, room_code: str) -> None:
    normalized_room = room_code.upper()
    await manager.connect(normalized_room, websocket)

    try:
        snapshot = await store.get_room_snapshot(normalized_room)
        await websocket.send_json({"type": "room_snapshot", "room": snapshot})

        while True:
            # Keep the websocket open for server push updates.
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(normalized_room, websocket)