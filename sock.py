from flask import Flask
from flask_socketio import SocketIO
from flask_misaka import Misaka
import dotenv, os

app = Flask(__name__)
dotenv.load_dotenv()
app.secret_key = os.getenv('FLASK_KEY')
socketio = SocketIO(app)
Misaka(app, no_intra_emphasis=True)