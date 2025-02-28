from flask_socketio import SocketIO
from flask import Flask
from flask_misaka import Misaka
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
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')