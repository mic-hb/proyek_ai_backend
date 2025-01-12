""" API for the game server. """

from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
from src.game.board import GameBoard

# Initialize Flask and Flask-SocketIO
app = Flask(__name__)
socketio = SocketIO(app)

# Initialize the game
game = GameBoard()


@app.route('/game/state', methods=['GET'])
def get_game_state():
    """
    Fetch the current game state including the board and valid moves.
    """
    game.calculate_valid_moves()
    return jsonify({
        'center_board': game.center_board,
        'left_wing': game.left_wing,
        'right_wing': game.right_wing
    })


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
    emit('game_state', {'center_board': game.center_board,
         'left_wing': game.left_wing, 'right_wing': game.right_wing})


@socketio.on('make_move')
def handle_make_move(data):
    """
    Handle the player's move via WebSocket and broadcast the new game state.
    """
    print(f"Move received: {data}")
    # Process the move (update the game state)

    # Recalculate valid moves and emit back the new state
    game.calculate_valid_moves()
    emit('game_state', {'center_board': game.center_board,
         'left_wing': game.left_wing, 'right_wing': game.right_wing})


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
