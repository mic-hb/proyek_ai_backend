""" This module contains the Room class representing a room in the game. """

from typing import List
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json


from src.game.game import Game
from src.game.player import Player

@dataclass_json
@dataclass
class Room:
    """
    A class to represent a room in the game.

    Attributes:
        code: str
            The code of the room.
        name: str
            The name of the room.
        is_private: bool
            Whether the room is private.
        all_players_ready: bool
            Whether all players are ready.
        game_state: Game
            The game state of the room.
    """
    code: str
    name: str
    is_private: bool
    all_players_ready: bool = False
    game_state: Game = field(default_factory=Game)

    def to_json(self) -> str:
        return self.to_json()
