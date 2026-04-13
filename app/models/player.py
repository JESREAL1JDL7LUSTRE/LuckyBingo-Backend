from pydantic import BaseModel, Field


class JoinRoomRequest(BaseModel):
	room_code: str = Field(min_length=4, max_length=12)
	player_name: str = Field(min_length=1, max_length=40)


class PlayerView(BaseModel):
	player_id: str
	player_name: str
	is_host: bool


class JoinRoomResponse(BaseModel):
	player_id: str
	room_code: str
	card: list[list[int | str]]
