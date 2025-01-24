from dataclasses import dataclass, field
from dataclasses_json import dataclass_json

from src.game.piece import Piece
from src.game.constants import CellTypes

@dataclass_json
@dataclass
class Cell:
    """
    A dataclass representing a cell on the game board.

    Attributes:
        piece: The piece on the cell.
        type: The type of the cell.
        valid_moves: The valid moves for the cell.
    """
    piece: Piece = field(default_factory=Piece)
    type: CellTypes = field(default=CellTypes.INVALID)
    valid_moves: list[tuple[int, int, str]] = field(default_factory=list)
