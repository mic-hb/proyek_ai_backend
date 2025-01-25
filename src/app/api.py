""" API for the game server. """

import json
from typing import Dict
import uuid

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room

from src.game.board import Board
from src.game.game import Game
from src.game.constants import PieceTypes
from src.game.player import Player
from src.game.room import Room

# Initialize Flask and Flask-SocketIO
app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app=app, cors_allowed_origins="*", logger=True)

# Store active rooms
rooms: Dict[str, Room] = {}


@app.route('/room/<room_code>/game/state', methods=['GET'])
def get_game_state(room_code: str) -> dict[str, Board]:
    """
    Fetch the current game state including the board and valid moves.
    """

    room: Room = rooms[room_code]
    game_state: Game = room.game_state

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


@app.route('/room/<room_code>/game/board', methods=['GET'])
def get_game_board(room_code: str) -> str:
    """
    Fetch the current game board.
    """
    room: Room = rooms[room_code]
    game_state: Game = room.game_state

    formatted_board = game_state.format_board()

    return formatted_board  # type: ignore


@app.route('/room/<room_code>/game/move', methods=['POST'])
def make_move(room_code: str):
    """
    Make a move by updating the board and sending the new state.
    The move data should be passed in the body (JSON).
    """
    move = request.json  # Expecting a move in the form: {"row": x, "col": y, "target_row": tr, "target_col": tc}

    room: Room = rooms[room_code]
    game_state: Game = room.game_state

    # Apply move here (update the game logic)
    # For simplicity, we just print it out for now
    print(f"Move: {move}")

    # You can call a method in your GameBoard class to handle the move logic

    game_state.calculate_valid_moves()  # Recalculate valid moves after the move
    return jsonify({'message': 'Move applied successfully!'})


@app.route('/room/<room_code>/game/reset', methods=['POST'])
def reset_game(room_code: str):
    """
    Reset the game to its initial state.
    """
    room: Room = rooms[room_code]
    game_state: Game = room.game_state

    game_state.reset()

    game_state_json: str = game_state.to_json()
    game_state_dict: dict[str, Board] = json.loads(game_state_json)
    socketio.emit('game_state', json.dumps(game_state_dict))

    return jsonify({'message': 'Game reset successfully!'})

@app.route('/rooms', methods=['GET'])
def get_rooms():
    """
    Fetch the current rooms.
    """
    room_list= [{
        'code': room.code,
        'name': room.name,
        'is_private': room.is_private,
        'all_players_ready': room.all_players_ready,
        'players': [player for player in room.game_state.players]
    } for room in rooms.values()]

    return jsonify({'rooms': room_list})

# WebSocket for real-time updates
@socketio.on('connect')
def handle_connect():
    """
    Handle new WebSocket connections. Send the initial game state.
    """
    print(f"Client connected, sid: {request.sid}")  # type: ignore
    print(f"Rooms: {socketio.server.manager.rooms.keys()}")  # type: ignore

    connection_response_data = {
        'you_are': {
            'sid': request.sid  # type: ignore
        },
    }

    emit('connection_response', json.dumps(connection_response_data))

    send_rooms()


@socketio.on('disconnect')
def handle_disconnect(reason):
    """
    Handle WebSocket disconnections.
    """
    print(f'Client disconnected, reason: {reason}')
    print(f'Player disconnected: {request.sid}')  # type: ignore

    for room in rooms.values():
        for player in room.game_state.players:
            if player.sid == request.sid:  # type: ignore
                room.game_state.players.remove(player)

                if len([p for p in room.game_state.players if p.piece_type != PieceTypes.BLANK]) == 2:
                    room.all_players_ready = True
                else:
                    room.all_players_ready = False

                room_json: str = room.to_json()
                room_dict: dict[str, str | bool | Game] = json.loads(room_json)

                response_data = {
                    'room': room_dict
                }

                emit('new_room_state', json.dumps(response_data), to=room.code,broadcast=True)

    send_rooms()



@socketio.on('create_room')
def handle_create_room(data: dict):
    room_code: str = str(uuid.uuid4())[:8]

    print(f"Creating room: private? {data['isPrivate']}")
    rooms[room_code] = Room(
        code=room_code,
        name=data['name'],
        is_private=bool(data['isPrivate']),
        game_state=Game()
    )
    join_room(room=room_code)

    room_json: str = rooms[room_code].to_json()
    room_dict: Dict[str, str | bool| Game]= json.loads(room_json)

    response_data = {
        'room': room_dict
    }

    emit('room_created', json.dumps(response_data))
    emit('new_room_state', json.dumps(response_data), to=room_code,broadcast=True)

    send_rooms()

@socketio.on('join_room')
def handle_join_room(data: dict):
    print(data)
    room_code: str = data['roomCode']
    if room_code not in rooms:
        emit('error', 'Room not found')
        return

    room = rooms[room_code]
    if len(room.game_state.players) >= 2:
        emit('room_full', 'Room is full')
        return

    join_room(room=room_code)

    room_json: str = room.to_json()
    room_dict: dict[str, str | bool | Game] = json.loads(room_json)

    response_data = {
        'room': room_dict
    }

    emit('room_joined', json.dumps(response_data))
    emit('new_room_state', json.dumps(response_data), to=room_code,broadcast=True)

    send_rooms()


@socketio.on('send_initial_player_data')
def initial_player_data(data: dict):
    """
    Initialize the player data.
    """
    print(f"Initial player data received: {request.sid}, {data}") # type: ignore

    room_code: str = data['roomCode']
    room: Room = rooms[room_code]
    game_state: Game = room.game_state

    player_sids: list[str] = [p.sid for p in game_state.players]

    if request.sid not in player_sids:  # type: ignore
        player = Player(
            name=data['name'],
            sid=request.sid,  # type: ignore
            piece_type=data['pieceType']
        )
        game_state.players.append(player)
    else:
        player: Player = next((p for p in game_state.players if p.sid == request.sid), None)  # type: ignore
        player.name = data['name']
        player.piece_type = data['pieceType']

    print(f"Players: {[{p.sid: [p.name,p.piece_type]} for p in game_state.players]}")

    room_json: str = room.to_json()
    room_dict: dict[str, Room] = json.loads(room_json)

    response_data = {
        'room': room_dict
    }

    emit('new_room_state', json.dumps(response_data), to=room_code,broadcast=True)

    send_rooms()

@socketio.on('send_player_data')
def update_player_data(data: dict):
    """
    Update the player data.
    """
    print(f"Player data received: {request.sid}, {data}") # type: ignore
    current_player: str = request.sid  # type: ignore

    room_code: str = data['roomCode']
    room: Room = rooms[room_code]
    game_state: Game = room.game_state

    for player in game_state.players:
        if player.sid == current_player:
            print(f"Changing player {player.name} piece type to {data['pieceType']}")
            player.piece_type = data['pieceType']
            player.initialize_pieces()

    print(f"{len([p for p in room.game_state.players if p.piece_type != PieceTypes.BLANK])} ready players: {[p.name for p in room.game_state.players if p.piece_type != PieceTypes.BLANK]}")
    if len([p for p in room.game_state.players if p.piece_type != PieceTypes.BLANK]) == 2:
        room.all_players_ready = True
    else:
        room.all_players_ready = False

    print(f"All players ready: {room.all_players_ready}")

    room_json: str = room.to_json()
    room_dict: dict[str, Room] = json.loads(room_json)

    response_data = {
        'room': room_dict
    }

    emit('new_room_state', json.dumps(response_data), to=room_code,broadcast=True)

    send_rooms()


@socketio.on('make_move')
def handle_make_move(data: dict):
    """
    Handle the player's move via WebSocket and broadcast the new game state.
    """
    print(f"Move received: {data}")

    room_code: str = data['roomCode']
    room: Room = rooms[room_code]
    game_state: Game = room.game_state

    if game_state.turn != data['playerPiece']['type']:
        emit('invalid_move', 'Not your turn!')
        return

    # Process the move (update the game state)
    game_state.make_move(data['playerName'], data['playerPiece'], data['row'], data['col'])

    # Recalculate valid moves and emit back the new state
    # game.calculate_valid_moves()

    game_state_json: str = game_state.to_json()
    game_state_dict: dict[str, Board | list[Player] | PieceTypes] = json.loads(game_state_json)

    response_data = {
        'game_state': game_state_dict
    }

    emit('update_game_state', json.dumps(response_data), to=room_code,broadcast=True)

def send_rooms():
    room_list= [{
        'code': room.code,
        'name': room.name,
        'is_private': room.is_private,
        'all_players_ready': room.all_players_ready,
        'players': [player.to_json() for player in room.game_state.players]
    } for room in rooms.values() if room.is_private == False]

    room_list_json: str = json.dumps(room_list)
    room_list_dict: list[dict[str, str | bool | list[Player]]] = json.loads(room_list_json)

    socketio.emit('new_rooms', room_list_dict)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8080)

