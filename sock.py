from flask import Flask
from flask_socketio import SocketIO
import dotenv, os

app = Flask(__name__)
dotenv.load_dotenv()
app.secret_key = os.getenv('FLASK_KEY')
socketio = SocketIO(app)