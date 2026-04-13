import asyncio
from uuid import uuid4

from fastapi import HTTPException

from app.services.bingo_logic import draw_number, generate_bingo_card, generate_room_code, validate_bingo


class InMemoryStore:
	def __init__(self) -> None:
		self.rooms: dict[str, dict] = {}
		self._lock = asyncio.Lock()

	async def create_room(self, host_name: str) -> tuple[str, str, list[list[int | str]]]:
		async with self._lock:
			room_code = self._new_room_code()
			host_id = str(uuid4())
			host_card = generate_bingo_card()

			self.rooms[room_code] = {
				"room_code": room_code,
				"host_id": host_id,
				"status": "waiting",
				"players": {
					host_id: {
						"player_id": host_id,
						"player_name": host_name,
						"is_host": True,
						"card": host_card,
					}
				},
				"called_numbers": [],
				"remaining_numbers": set(range(1, 76)),
				"current_number": None,
				"winner_id": None,
			}
			return room_code, host_id, host_card

	async def join_room(self, room_code: str, player_name: str) -> tuple[str, list[list[int | str]]]:
		async with self._lock:
			room = self._get_room_or_404(room_code)
			if room["status"] == "finished":
				raise HTTPException(status_code=400, detail="Game already finished")

			player_id = str(uuid4())
			card = generate_bingo_card()
			room["players"][player_id] = {
				"player_id": player_id,
				"player_name": player_name,
				"is_host": False,
				"card": card,
			}
			return player_id, card

	async def call_number(self, room_code: str, host_id: str) -> int:
		async with self._lock:
			room = self._get_room_or_404(room_code)
			if room["host_id"] != host_id:
				raise HTTPException(status_code=403, detail="Only the host can call numbers")
			if room["status"] == "finished":
				raise HTTPException(status_code=400, detail="Game already finished")

			number = draw_number(room["remaining_numbers"])
			room["status"] = "in_progress"
			room["current_number"] = number
			room["called_numbers"].append(number)
			return number

	async def claim_bingo(self, room_code: str, player_id: str) -> bool:
		async with self._lock:
			room = self._get_room_or_404(room_code)
			player = room["players"].get(player_id)
			if not player:
				raise HTTPException(status_code=404, detail="Player not found in room")
			if room["winner_id"]:
				return room["winner_id"] == player_id

			is_winner = validate_bingo(player["card"], set(room["called_numbers"]))
			if is_winner:
				room["status"] = "finished"
				room["winner_id"] = player_id
			return is_winner

	async def get_room_snapshot(self, room_code: str) -> dict:
		async with self._lock:
			room = self._get_room_or_404(room_code)
			return self._room_to_snapshot(room)

	def _new_room_code(self) -> str:
		while True:
			code = generate_room_code()
			if code not in self.rooms:
				return code

	def _get_room_or_404(self, room_code: str) -> dict:
		room = self.rooms.get(room_code.upper())
		if not room:
			raise HTTPException(status_code=404, detail="Room not found")
		return room

	def _room_to_snapshot(self, room: dict) -> dict:
		players = [
			{
				"player_id": player_data["player_id"],
				"player_name": player_data["player_name"],
				"is_host": player_data["is_host"],
			}
			for player_data in room["players"].values()
		]

		return {
			"room_code": room["room_code"],
			"host_id": room["host_id"],
			"status": room["status"],
			"players": players,
			"called_numbers": room["called_numbers"],
			"current_number": room["current_number"],
			"winner_id": room["winner_id"],
		}


store = InMemoryStore()
