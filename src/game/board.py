from dataclasses import dataclass, field
from typing import List
from dataclasses_json import dataclass_json

from src.game.cell import Cell

@dataclass_json
@dataclass
class Board:
    """A dataclass representing a board in the game."""
    cells: List[List[Cell]] = field(default_factory=list)
