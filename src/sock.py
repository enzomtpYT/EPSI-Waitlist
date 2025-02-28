from flask_socketio import SocketIO
from flask import Flask, request
from flask_misaka import Misaka
from flask_cors import CORS
import dotenv, os
from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})


app = Flask(__name__)
dotenv.load_dotenv()
app.secret_key = os.getenv('FLASK_KEY')
Misaka(app, no_intra_emphasis=True)
if os.name == 'nt':
    async_mode = 'threading'
else:
    async_mode = 'gevent'


socketio = SocketIO(app, cors_allowed_origins="*", async_mode=async_mode, logger=True, engineio_logger=True)
@socketio.on('connect')
def test_connect():
    app.logger.info(f'Client connected {request.sid}')
@socketio.on('disconnect')
def test_disconnect():
    app.logger.info(f'Client disconnected {request.sid}')
CORS(app, resources={r"/*": {"origins": "*"}})