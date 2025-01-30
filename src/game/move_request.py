""" Move Request class module """

import json
from dataclasses import dataclass, field, asdict
from dataclasses_json import dataclass_json
from src.game.game import Game


@dataclass_json
@dataclass
class MoveRequest:
    game_state: Game
    algorithm: int
    player_name: str = field(default="")

    def __to_json__(self) -> str:
        return json.dumps(asdict(self))
