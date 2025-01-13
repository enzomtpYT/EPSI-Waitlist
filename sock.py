from flask import Flask, request
from flask_socketio import SocketIO, send

app = Flask(__name__)
socketio = SocketIO(app)