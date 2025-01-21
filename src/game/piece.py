""" Piece class module """

import json
from dataclasses import dataclass, field, asdict
from dataclasses_json import dataclass_json
from src.game.constants import PieceTypes


@dataclass_json
@dataclass
class PositionVector:
    x: int
    y: int

    def __to_json__(self) -> str:
        return json.dumps(asdict(self))

    @staticmethod
    def from_json(json_str: str) -> 'PositionVector':
        return PositionVector(**json.loads(json_str))

    def __add__(self, other: 'PositionVector') -> 'PositionVector':
        return PositionVector(x=self.x + other.x, y=self.y + other.y)

    def __sub__(self, other: 'PositionVector') -> 'PositionVector':
        return PositionVector(x=self.x - other.x, y=self.y - other.y)

    def __mul__(self, other: int) -> 'PositionVector':
        return PositionVector(x=self.x * other, y=self.y * other)

    # def __eq__(self, other: 'PositionVector') -> bool:
    #     return self.x == other.x and self.y == other.y

    # def __ne__(self, other: 'PositionVector') -> bool:
    #     return self.x != other.x or self.y != other.y

    def __lt__(self, other: 'PositionVector') -> bool:
        return self.x < other.x and self.y < other.y

    def __le__(self, other: 'PositionVector') -> bool:
        return self.x <= other.x and self.y <= other.y

    def __gt__(self, other: 'PositionVector') -> bool:
        return self.x > other.x and self.y > other.y

    def __ge__(self, other: 'PositionVector') -> bool:
        return self.x >= other.x and self.y >= other.y

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

@dataclass_json
@dataclass
class Piece:
    """
    A class to represent a piece in the game.

    Attributes
    ----------
    """
    position: PositionVector = field(default_factory=lambda: PositionVector(x=-1, y=-1))
    type: PieceTypes = field(default=PieceTypes.BLANK)
    valid_moves: list[PositionVector] = field(default_factory=list)

    def to_json(self) -> str:
        """
        Convert the piece object to a JSON string.

        Returns
        -------
        str
            The JSON string representing the piece object.
        """
        return json.dumps(asdict(self))

    @staticmethod
    def from_json(json_str: str) -> 'Piece':
        """
        Create a piece object from a JSON string.

        Parameters
        ----------
        json_str : str
            The JSON string representing the piece object.

        Returns
        -------
        Piece
            The piece object created from the JSON string.
        """
        return Piece(**json.loads(json_str))
