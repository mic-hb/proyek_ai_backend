""" Move Request class module """

import json
from dataclasses import dataclass, field, asdict
from dataclasses_json import dataclass_json
from src.game.game import Game
from src.game.piece import Piece


@dataclass_json
@dataclass
class SuggestedMove:
    message: str
    player_name: str
    player_piece: Piece
    row: int
    col: int

    def to_json(self) -> str:
        return json.dumps(asdict(self))
