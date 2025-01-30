""" API for the AI server. """

import json

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit

from src.game.move_request import MoveRequest
from src.game.suggested_move import SuggestedMove
from src.game.piece import Piece, PositionVector
from src.game.game import Game
from src.game.cell import Cell
from src.game.player import Player
from src.ai.AI import generate_suggested_move


# Initialize Flask and Flask-SocketIO
app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app=app, cors_allowed_origins="*", logger=True)

# WebSocket for real-time updates
@socketio.on('connect')
def handle_connect():
    """
    Handle new WebSocket connections.
    """
    print(f"Client connected, sid: {request.sid}")  # type: ignore

    emit('init', "Hello, world!")

@socketio.on('disconnect')
def handle_disconnect(reason):
    """
    Handle WebSocket disconnections.
    """
    print(f"Client disconnected, sid: {request.sid}, reason: {reason}")  # type: ignore

    emit('disconnected', "A client has disconnected", broadcast=True)

@socketio.on('move_request')
def handle_move_request(data):
    """
    Handle move requests from clients.
    """
    print(f"Received move request")

    # move_request: MoveRequest = MoveRequest.from_json(json.dumps(data))
    # move_request: MoveRequest = MoveRequest.from_dict(data)
    move_request: MoveRequest = parse_move_request(data=data)

    suggested_move: SuggestedMove = generate_suggested_move(move_request=move_request)

    suggested_move_json: str = suggested_move.to_json()
    suggested_move_dict: dict[str, str | Piece | int] = json.loads(suggested_move_json)

    # Emit the move
    emit('suggest_move', json.dumps(suggested_move_dict))

def parse_move_request(data: dict) -> MoveRequest:
    """
    Parse a move request from a dictionary.

    Parameters
    ----------
    data : dict
        The dictionary containing the move request data.

    Returns
    -------
    MoveRequest
        The move request object created from the dictionary.
    """
    player_name = data['playerName']

    board_dict = data['gameState']['board']
    board = [
        [
            Cell(Piece(
                cell['piece']['id'],
                PositionVector(cell['piece']['position']['x'], cell['piece']['position']['y']),
                cell['piece']['type'],
                cell['piece']['validMoves'],
            ), cell['type']) for cell in row
        ] for row in board_dict
    ]

    players_dict = data['gameState']['players']
    players = [
        Player(
            player['name'],
            player['sid'],
            player['pieceType'],
            [Piece(
                piece['id'],
                PositionVector(piece['position']['x'], piece['position']['y']),
                piece['type'],
                piece['validMoves'],
            ) for piece in player['pieces']],
            player['score'],
        ) for player in players_dict
    ]

    game_state = Game()
    game_state.board = board
    game_state.players = players
    game_state.turn = data['gameState']['turn']

    return MoveRequest(game_state, player_name)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
