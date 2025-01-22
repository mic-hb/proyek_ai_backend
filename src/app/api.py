""" API for the game server. """

import json

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit

from src.game.board import Board, Game
from src.game.constants import PieceTypes

# Initialize Flask and Flask-SocketIO
app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app=app, cors_allowed_origins="*", logger=True)

# Initialize the game
game_state = Game()

@app.route('/game/state', methods=['GET'])
def get_game_state() -> dict[str, Board]:
    """
    Fetch the current game state including the board and valid moves.
    """
    game_state.calculate_valid_moves()

    game_state_json: str = game_state.to_json()
    game_state_dict: dict[str, Board] = json.loads(game_state_json)

    players_json = json.dumps(obj=[player.to_json() for player in game_state.players])
    players_dict: list[dict[str, str | PieceTypes | int]
                       ] = json.loads(players_json)

    data = {
        'players': players_dict,
        'game_state': game_state_dict
    }

    return data


@app.route('/game/board', methods=['GET'])
def get_game_board() -> Board:
    """
    Fetch the current game board.
    """
    formatted_board = game_state.format_board()

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

    game_state.calculate_valid_moves()  # Recalculate valid moves after the move
    return jsonify({'message': 'Move applied successfully!'})


@app.route('/game/reset', methods=['POST'])
def reset_game():
    """
    Reset the game to its initial state.
    """
    game_state.reset()

    game_state_json: str = game_state.to_json()
    game_state_dict: dict[str, Board] = json.loads(game_state_json)
    socketio.emit('game_state', json.dumps(game_state_dict))

    return jsonify({'message': 'Game reset successfully!'})



# WebSocket for real-time updates
@socketio.on('connect')
def handle_connect():
    """
    Handle new WebSocket connections. Send the initial game state.
    """
    print(f"Client connected, sid: {request.sid}")  # type: ignore

    game_state_json: str = game_state.to_json()
    game_state_dict: dict[str, Board] = json.loads(game_state_json)

    players_json = json.dumps(obj=[player.to_json() for player in game_state.players])
    players_dict: list[dict[str, str | PieceTypes | int]
                       ] = json.loads(players_json)

    print(f"Players: {players_dict}")

    connection_response_data = {
        'you_are': {
            'sid': request.sid  # type: ignore
        },
        'players': players_dict,
        'game_state': game_state_dict
    }

    emit('init_game', json.dumps(connection_response_data))


@socketio.on('make_move')
def handle_make_move(data: dict):
    """
    Handle the player's move via WebSocket and broadcast the new game state.
    """
    print(f"Move received: {data}")

    if game_state.turn != data['player_piece']['type']:
        emit('invalid_move', 'Not your turn!')
        return

    # Process the move (update the game state)
    game_state.make_move(data['player_name'], data['player_piece'],
                          data['row'], data['col'])

    # Recalculate valid moves and emit back the new state
    # game.calculate_valid_moves()

    game_state_json: str = game_state.to_json()
    game_state_dict: dict[str, Board] = json.loads(game_state_json)

    players_json = json.dumps(obj=[player.to_json() for player in game_state.players])
    players_dict: list[dict[str, str | PieceTypes | int]
                       ] = json.loads(players_json)

    response_data = {
        'players': players_dict,
        'game_state': game_state_dict
    }

    emit('game_state', json.dumps(response_data), broadcast=True)

@socketio.on('send_initial_player_data')
def initial_player_data(data: dict):
    """
    Initialize the player data.
    """
    print(f"Player data received: {data}")
    current_player_name = data['name']

    if game_state.players[0].name == "":
        game_state.players[0].name = current_player_name
        game_state.players[0].sid = request.sid  # type: ignore
    elif game_state.players[1].name == "":
        game_state.players[1].name = current_player_name
        game_state.players[1].sid = request.sid  # type: ignore
    else:
        emit('game_full', json.dumps({'message': 'Game is full!'}))

    game_state_json: str = game_state.to_json()
    game_state_dict: dict[str, Board] = json.loads(game_state_json)

    players_json = json.dumps(obj=[player.to_json() for player in game_state.players])
    players_dict: list[dict[str, str | PieceTypes | int]
                       ] = json.loads(players_json)

    print(f"Players: {players_dict}")

    response_data = {
        'players': players_dict
    }

    emit('player_state', json.dumps(response_data), broadcast=True)


@socketio.on('send_player_data')
def update_player_data(data: dict):
    """
    Update the player data.
    """
    print(f"Player data received: {data}")
    current_player = data['name']

    for player in game_state.players:
        if player.name == current_player:
            player.piece_type = data['pieceType']
            player.score = data['score']
            player.initialize_pieces()


    game_state_json: str = game_state.to_json()
    game_state_dict: dict[str, Board] = json.loads(game_state_json)

    players_json = json.dumps(obj=[player.to_json() for player in game_state.players])
    players_dict: list[dict[str, str | PieceTypes | int]
                       ] = json.loads(players_json)

    response_data = {
        'players': players_dict
    }

    emit('player_state', json.dumps(response_data), broadcast=True)

@socketio.on('disconnect')
def handle_disconnect(reason):
    """
    Handle WebSocket disconnections.
    """
    print(f'Client disconnected, reason: {reason}')
    print(f'Player disconnected: {request.sid}')  # type: ignore

    print(f"Players: {game_state.players}")

    disconnected_players = 0
    for player in game_state.players:
        if player.sid == "":
            disconnected_players += 1
        if player.sid == request.sid:  # type: ignore
            print(f"Player {player.name}, {player.sid} disconnected.")
            player.name = ""
            player.sid = ""
            player.piece_type = PieceTypes.BLANK
            player.score = 0
            disconnected_players += 1
            break

    if disconnected_players == len(game_state.players):
        game_state.reset()

    print(f"Players: {game_state.players}")

    players_json = json.dumps(obj=[player.to_json() for player in game_state.players])
    players_dict: list[dict[str, str | PieceTypes | int]
                       ] = json.loads(players_json)

    response_data = {
        'players': players_dict
    }

    emit('player_state', json.dumps(response_data), broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
