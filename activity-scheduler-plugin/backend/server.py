import eventlet
eventlet.monkey_patch()

from flask import Flask, request
from flask_socketio import SocketIO
from flask_cors import CORS
from activity import decompose_task, execute_task
import sys
from io import StringIO

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet', logger=True, engineio_logger=True)

class SocketIOHandler(StringIO):
    def write(self, text):
        if text.strip():  # Only emit non-empty strings
            socketio.emit('log', {'message': text})
        return super().write(text)

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('decompose_task')
def handle_decompose(data):
    try:
        # Redirect stdout to our custom handler
        old_stdout = sys.stdout
        sys.stdout = SocketIOHandler()
        
        activity = data.get('activity')
        if not activity:
            socketio.emit('error', {'message': 'No activity provided'})
            return
            
        tasks = decompose_task(activity)
        socketio.emit('tasks', {'tasks': tasks})
    except Exception as e:
        socketio.emit('error', {'message': str(e)})
    finally:
        # Restore stdout
        sys.stdout = old_stdout

@socketio.on('execute_task')
def handle_execute(data):
    try:
        # Redirect stdout to our custom handler
        old_stdout = sys.stdout
        sys.stdout = SocketIOHandler()
        
        task = data.get('task')
        if not task:
            socketio.emit('error', {'message': 'No task provided'})
            return
            
        result = execute_task(task)
        socketio.emit('message', {'message': result})
    except Exception as e:
        socketio.emit('error', {'message': str(e)})
    finally:
        # Restore stdout
        sys.stdout = old_stdout

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)
