""" Player class module """

import json
from dataclasses import dataclass, field, asdict
from dataclasses_json import dataclass_json
from src.game.constants import PieceTypes
from src.game.piece import Piece


@dataclass_json
@dataclass
class Player:
    """
    A class to represent a player in the game.

    Attributes
    ----------
    name : str
        The name of the player.
    socket_id : str
        The socket ID of the player.
    piece_types : PieceTypes
        The piece type of the player.
    score : int
        The score of the player.
    """

    name: str = field(default="")
    sid: str = field(default="")
    piece_type: PieceTypes = field(default=PieceTypes.BLANK)
    pieces: list[Piece] = field(default_factory=list)
    score: int = field(default=0)

    # def __init__(self):
    #     pass

    def to_json(self) -> str:
        """
        Convert the player object to a JSON string.

        Returns
        -------
        str
            The JSON string representing the player object.
        """
        return json.dumps(asdict(self))

    @staticmethod
    def from_json(json_str: str) -> 'Player':
        """
        Create a player object from a JSON string.

        Parameters
        ----------
        json_str : str
            The JSON string representing the player object.

        Returns
        -------
        Player
            The player object created from the JSON string.
        """
        return Player(**json.loads(json_str))

    def initialize_pieces(self) -> None:
        """
        Initialize the player's pieces.
        """
        pieces = []
        for _ in range(2) if self.piece_type == PieceTypes.MACAN else range(8):
            pieces.append(Piece(type=self.piece_type))

        self.pieces = pieces
