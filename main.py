"""Main module."""
from src.app.api import app, socketio
from src.app.ai import app as ai_app, socketio as ai_socketio
import threading

def run_game_server():
    socketio.run(app, host='0.0.0.0', port=8080)

def run_ai_server():
    ai_socketio.run(ai_app, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    # Create threads for each server
    game_thread = threading.Thread(target=run_game_server)
    ai_thread = threading.Thread(target=run_ai_server)

    # Start both servers
    ai_thread.start()
    game_thread.start()

    # Wait for both threads to complete (they won't, as they run forever)
    ai_thread.join()
    game_thread.join()
