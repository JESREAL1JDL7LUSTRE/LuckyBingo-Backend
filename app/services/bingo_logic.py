import random
import string

from app.core.config import MAX_BINGO_NUMBER, MIN_BINGO_NUMBER, ROOM_CODE_LENGTH


def generate_room_code(length: int = ROOM_CODE_LENGTH) -> str:
	alphabet = string.ascii_uppercase + string.digits
	return "".join(random.choice(alphabet) for _ in range(length))


def generate_bingo_card() -> list[list[int | str]]:
	card: list[list[int | str]] = []
	column_ranges = [
		range(1, 16),
		range(16, 31),
		range(31, 46),
		range(46, 61),
		range(61, 76),
	]

	columns: list[list[int]] = [random.sample(list(col_range), 5) for col_range in column_ranges]

	for row_index in range(5):
		row = [columns[col_index][row_index] for col_index in range(5)]
		card.append(row)

	card[2][2] = "FREE"
	return card


def draw_number(remaining_numbers: set[int]) -> int:
	if not remaining_numbers:
		raise ValueError("No more numbers available")

	selected = random.choice(list(remaining_numbers))
	remaining_numbers.remove(selected)
	return selected


def validate_bingo(card: list[list[int | str]], called_numbers: set[int]) -> bool:
	line_values: list[list[int | str]] = []

	line_values.extend(card)

	for column_index in range(5):
		line_values.append([card[row_index][column_index] for row_index in range(5)])

	line_values.append([card[index][index] for index in range(5)])
	line_values.append([card[index][4 - index] for index in range(5)])

	def is_marked(value: int | str) -> bool:
		if value == "FREE":
			return True
		return isinstance(value, int) and MIN_BINGO_NUMBER <= value <= MAX_BINGO_NUMBER and value in called_numbers

	return any(all(is_marked(value) for value in line) for line in line_values)
