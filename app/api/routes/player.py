from fastapi import APIRouter

from app.models.player import JoinRoomRequest, JoinRoomResponse
from app.models.room import RoomSnapshot
from app.state.store import store
from app.websockets.connection_manager import manager

router = APIRouter(prefix="/players", tags=["players"])


@router.post("/join", response_model=JoinRoomResponse)
async def join_room(payload: JoinRoomRequest) -> JoinRoomResponse:
	room_code = payload.room_code.upper()
	player_id, card = await store.join_room(room_code, payload.player_name)

	snapshot = await store.get_room_snapshot(room_code)
	await manager.broadcast_room(room_code, {"type": "room_update", "room": snapshot})

	return JoinRoomResponse(player_id=player_id, room_code=room_code, card=card)


@router.get("/{room_code}", response_model=RoomSnapshot)
async def get_room_players_view(room_code: str) -> RoomSnapshot:
	snapshot = await store.get_room_snapshot(room_code.upper())
	return RoomSnapshot(**snapshot)
