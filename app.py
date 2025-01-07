from flask import Flask
import os
from routes.index import index
from routes.admin import admin
from routes.liste import liste
from routes.manage_candidate import manage_candidate
from routes.candidate import candidate
from routes.create_candidate import create_candidate_bp
from flask import render_template
from flask import session

app = Flask(__name__)

app.secret_key = os.urandom(24)

app.register_blueprint(create_candidate_bp)

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
app.add_url_rule("/liste/live", "liste", liste)
app.add_url_rule("/admin", "admin", admin)
app.add_url_rule("/admin/manage_candidate", "manage_candidate", manage_candidate)
app.add_url_rule("/admin/manage_candidate/candidate", "candidate", candidate)

if __name__ == "__main__":
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    app.run(host="127.0.0.1", port=8080, debug=debug_mode)

@app.route('/database', methods=['GET', 'POST'])
def database():
    query = []
    for i in session.query(models.BlogPost):
        query.append((i.title, i.post, i.date))
    return render_template('database.html', query = query)