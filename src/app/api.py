""" API for the game server. """

import json

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit

from src.game.board import Board, GameBoard, Pieces

# Initialize Flask and Flask-SocketIO
app = Flask(__name__)
socketio = SocketIO(app)

CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize the game
game = GameBoard()


@app.route('/game/state', methods=['GET'])
def get_game_state() -> dict[str, Board]:
    """
    Fetch the current game state including the board and valid moves.
    """
    game.calculate_valid_moves()

    game_state_json: str = game.to_json()
    game_state_dict: dict[str, Board] = json.loads(game_state_json)
    return game_state_dict


@app.route('/game/board', methods=['GET'])
def get_game_board() -> Board:
    """
    Fetch the current game board.
    """
    formatted_board = game.format_board()

    return formatted_board  # type: ignore


@app.route('/game/move', methods=['POST'])
def make_move():
    """
    Make a move by updating the board and sending the new state.
    The move data should be passed in the body (JSON).
    """
    move = request.json  # Expecting a move in the form: {"row": x, "col": y, "target_row": tr, "target_col": tc}

    # Apply move here (update the game logic)
    # For simplicity, we just print it out for now
    print(f"Move: {move}")

    # You can call a method in your GameBoard class to handle the move logic

    game.calculate_valid_moves()  # Recalculate valid moves after the move
    return jsonify({'message': 'Move applied successfully!'})


# WebSocket for real-time updates
@socketio.on('connect')
def handle_connect():
    """
    Handle new WebSocket connections. Send the initial game state.
    """
    print("Client connected")
    # print(f"game: {game}")
    # emit('game_state', {'center_board': game.center_board,
    #      'left_wing': game.left_wing, 'right_wing': game.right_wing})
    emit('game_state', game.to_json())


@socketio.on('make_move')
def handle_make_move(data: dict):
    """
    Handle the player's move via WebSocket and broadcast the new game state.
    """
    print(f"Move received: {data}")
    # Process the move (update the game state)
    game.make_move(data['player'], data['board_type'],
                   data['row'], data['col'])

    print(game.format_board())
    # Recalculate valid moves and emit back the new state
    # game.calculate_valid_moves()
    emit('game_state', game.to_json())


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
