from fastapi import APIRouter, HTTPException

from app.models.room import (
	CallNumberRequest,
	ClaimBingoRequest,
	CreateRoomRequest,
	CreateRoomResponse,
	RoomSnapshot,
)
from app.state.store import store
from app.websockets.connection_manager import manager

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.post("", response_model=CreateRoomResponse)
async def create_room(payload: CreateRoomRequest) -> CreateRoomResponse:
	room_code, host_id, host_card = await store.create_room(payload.host_name)
	snapshot = await store.get_room_snapshot(room_code)
	return CreateRoomResponse(player_id=host_id, room_code=room_code, card=host_card, room=RoomSnapshot(**snapshot))


@router.get("/{room_code}", response_model=RoomSnapshot)
async def get_room(room_code: str) -> RoomSnapshot:
	snapshot = await store.get_room_snapshot(room_code.upper())
	return RoomSnapshot(**snapshot)


@router.post("/{room_code}/call-number")
async def call_number(room_code: str, payload: CallNumberRequest) -> dict:
	normalized_room = room_code.upper()
	try:
		number = await store.call_number(normalized_room, payload.host_id)
	except HTTPException as exc:
		if exc.status_code == 400 and exc.detail == "No more numbers available":
			snapshot = await store.get_room_snapshot(normalized_room)
			await manager.broadcast_room(
				normalized_room,
				{
					"type": "room_update",
					"room": snapshot,
				},
			)
		raise
	snapshot = await store.get_room_snapshot(normalized_room)
	await manager.broadcast_room(
		normalized_room,
		{
			"type": "number_called",
			"number": number,
			"room": snapshot,
		},
	)
	return {"number": number, "room": snapshot}


@router.post("/{room_code}/claim-bingo")
async def claim_bingo(room_code: str, payload: ClaimBingoRequest) -> dict:
	normalized_room = room_code.upper()
	is_valid = await store.claim_bingo(normalized_room, payload.player_id)
	snapshot = await store.get_room_snapshot(normalized_room)
	await manager.broadcast_room(
		normalized_room,
		{
			"type": "bingo_claim",
			"is_valid": is_valid,
			"claimed_by": payload.player_id,
			"room": snapshot,
		},
	)
	return {"is_valid": is_valid, "room": snapshot}
