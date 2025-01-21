from enum import IntEnum
from typing import List, TypeAlias

class PieceTypes(IntEnum):
    """An enumeration representing the player types."""
    INVALID = 9
    BLANK = 0
    MACAN = 1
    UWONG = 2


class CellTypes(IntEnum):
    """An enumeration representing the cell types."""
    INVALID = 0
    ALL_DIRECTIONS = 8
    FOUR_DIRECTIONS = 4
    SPECIAL = 3


PossibleMoves: TypeAlias = List[tuple[int, int, str]]
