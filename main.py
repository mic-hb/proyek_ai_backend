"""Main module."""
from src.app.api import app, socketio
from src.app.ai import app as ai_app, socketio as ai_socketio

if __name__ == '__main__':
    ai_socketio.run(ai_app, host='0.0.0.0', port=5000)
    socketio.run(app, host='0.0.0.0', port=8080)
