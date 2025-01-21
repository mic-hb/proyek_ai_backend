""" Piece class module """

import json
from dataclasses import dataclass, field, asdict
from dataclasses_json import dataclass_json
from src.game.board import PieceTypes


@dataclass_json
@dataclass
class Piece:
    """
    A class to represent a piece in the game.

    Attributes
    ----------
    """
    position: tuple[int, int] = field(default=(0, 0))
    piece_type: PieceTypes = field(default=PieceTypes.BLANK)
    valid_moves: list[tuple[int, int]] = field(default_factory=list)


    def __init__(self, position: tuple[int, int], piece_type: PieceTypes):
        self.position = position
        self.piece_type = piece_type

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
