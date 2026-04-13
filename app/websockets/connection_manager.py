from collections import defaultdict

from fastapi import WebSocket


class ConnectionManager:
	def __init__(self) -> None:
		self._connections: dict[str, set[WebSocket]] = defaultdict(set)

	async def connect(self, room_code: str, websocket: WebSocket) -> None:
		await websocket.accept()
		self._connections[room_code.upper()].add(websocket)

	def disconnect(self, room_code: str, websocket: WebSocket) -> None:
		normalized = room_code.upper()
		if normalized in self._connections:
			self._connections[normalized].discard(websocket)
			if not self._connections[normalized]:
				self._connections.pop(normalized, None)

	async def broadcast_room(self, room_code: str, payload: dict) -> None:
		normalized = room_code.upper()
		dead_connections: list[WebSocket] = []

		for websocket in self._connections.get(normalized, set()):
			try:
				await websocket.send_json(payload)
			except Exception:
				dead_connections.append(websocket)

		for websocket in dead_connections:
			self.disconnect(normalized, websocket)


manager = ConnectionManager()
