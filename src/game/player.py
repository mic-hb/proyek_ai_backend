""" Player class module """

import json
from dataclasses import dataclass, field, asdict
from dataclasses_json import dataclass_json
from src.game.board import Pieces


@dataclass_json
@dataclass
class Player:
    """
    A class to represent a player in the game.

    Attributes
    ----------
    name : str
        The name of the player.
    score : int
        The score of the player.
    """

    name: str = field(default="")
    socket_id: str = field(default="")
    piece: Pieces = field(default=Pieces.BLANK)
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
