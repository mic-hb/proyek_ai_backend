""" API for the game server. """

import json

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit

from src.game.board import Board, Pieces, GameBoard
from src.game.player import Player

# Initialize Flask and Flask-SocketIO
app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app=app, cors_allowed_origins="*", logger=True)

# Initialize the game
board_state = GameBoard()
players: list[Player] = [Player(), Player()]


@app.route('/game/state', methods=['GET'])
def get_game_state() -> dict[str, Board]:
    """
    Fetch the current game state including the board and valid moves.
    """
    board_state.calculate_valid_moves()

    board_state_json: str = board_state.to_json()
    board_state_dict: dict[str, Board] = json.loads(board_state_json)

    players_json = json.dumps(obj=[player.to_json() for player in players])
    players_dict: list[dict[str, str | Pieces | int]
                       ] = json.loads(players_json)

    game_state = {
        'players': players_dict,
        'board_state': board_state_dict
    }

    return game_state


@app.route('/game/board', methods=['GET'])
def get_game_board() -> Board:
    """
    Fetch the current game board.
    """
    formatted_board = board_state.format_board()

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

    board_state.calculate_valid_moves()  # Recalculate valid moves after the move
    return jsonify({'message': 'Move applied successfully!'})


@app.route('/game/reset', methods=['POST'])
def reset_game():
    """
    Reset the game to its initial state.
    """
    board_state.reset()

    game_state_json: str = board_state.to_json()
    game_state_dict: dict[str, Board] = json.loads(game_state_json)
    socketio.emit('game_state', json.dumps(game_state_dict))

    return jsonify({'message': 'Game reset successfully!'})

# WebSocket for real-time updates


@socketio.on('connect')
def handle_connect(auth):
    """
    Handle new WebSocket connections. Send the initial game state.
    """
    print(f"Client connected, {auth}")

    current_player = ''
    if players[0].name == "":
        current_player = 'player1'
        players[0].name = current_player
    elif players[1].name == "":
        current_player = 'player2'
        players[1].name = current_player
    else:
        emit('game_full', json.dumps({'message': 'Game is full!'}))

    board_state_json: str = board_state.to_json()
    board_state_dict: dict[str, Board] = json.loads(board_state_json)

    players_json = json.dumps(obj=[player.to_json() for player in players])
    players_dict: list[dict[str, str | Pieces | int]
                       ] = json.loads(players_json)

    game_state = {
        'you_are': current_player,
        'players': players_dict,
        'board_state': board_state_dict
    }

    emit('init_game', json.dumps(game_state))


@socketio.on('make_move')
def handle_make_move(data: dict):
    """
    Handle the player's move via WebSocket and broadcast the new game state.
    """
    print(f"Move received: {data}")
    # Process the move (update the game state)
    board_state.make_move(data['player'], data['board_type'],
                          data['row'], data['col'])

    # Recalculate valid moves and emit back the new state
    # game.calculate_valid_moves()

    board_state_json: str = board_state.to_json()
    board_state_dict: dict[str, Board] = json.loads(board_state_json)

    players_json = json.dumps(obj=[player.to_json() for player in players])
    players_dict: list[dict[str, str | Pieces | int]
                       ] = json.loads(players_json)

    game_state = {
        'players': players_dict,
        'board_state': board_state_dict
    }

    emit('game_state', json.dumps(game_state), broadcast=True)


@socketio.on('send_player_data')
def update_player_data(data: dict):
    """
    Update the player data.
    """
    print(f"Player data received: {data}")
    current_player = data['name']

    for player in players:
        if player.name == current_player:
            player.piece = data['piece']
            player.score = data['score']

    board_state_json: str = board_state.to_json()
    board_state_dict: dict[str, Board] = json.loads(board_state_json)

    players_json = json.dumps(obj=[player.to_json() for player in players])
    players_dict: list[dict[str, str | Pieces | int]
                       ] = json.loads(players_json)

    game_state = {
        'players': players_dict
    }

    emit('player_state', json.dumps(game_state), broadcast=True)


@socketio.on('disconnect')
def handle_disconnect(reason):
    """
    Handle WebSocket disconnections.
    """
    print(f'Client disconnected, reason: {reason}')

    players[0] = Player()
    players[1] = Player()


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
