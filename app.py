from flask import Flask
import os
from routes.index import index
from routes.admin import admin
from routes.liste import liste
from routes.liste import live
from routes.create_candidate import create_candidate
from routes.manage_candidate import manage_candidate
from routes.candidate import candidate

app = Flask(__name__)

custom_route_names = {

    "/": "Accueil",
    "/admin": "Admin",
    "/liste": "Liste"
}

@app.context_processor
def inject_routes():
    return dict(custom_route_names=custom_route_names)

app.add_url_rule("/", "index", index)
app.add_url_rule("/liste", "liste", liste)
app.add_url_rule("/liste/data-live", "live", live)
app.add_url_rule("/admin", "admin", admin)
app.add_url_rule("/admin/create_candidate", "create_candidate", create_candidate)
app.add_url_rule("/admin/manage_candidate", "manage_candidate", manage_candidate)
app.add_url_rule("/admin/manage_candidate/candidate", "candidate", candidate)

if __name__ == "__main__":
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    app.run(host="127.0.0.1", port=8080, debug=debug_mode)