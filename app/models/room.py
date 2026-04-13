from typing import Literal

from pydantic import BaseModel, Field

from app.models.player import PlayerView


class CreateRoomRequest(BaseModel):
	host_name: str = Field(min_length=1, max_length=40)


class CallNumberRequest(BaseModel):
	host_id: str


class ClaimBingoRequest(BaseModel):
	player_id: str


class RoomSnapshot(BaseModel):
	room_code: str
	host_id: str
	status: Literal["waiting", "in_progress", "finished"]
	players: list[PlayerView]
	called_numbers: list[int]
	current_number: int | None
	winner_id: str | None


class CreateRoomResponse(BaseModel):
	player_id: str
	room_code: str
	card: list[list[int | str]]
	room: RoomSnapshot
