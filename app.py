from flask import Flask, render_template, session
import os
from routes.index import index_bp
from routes.admin import admin_bp
from routes.liste import liste_bp
from routes.event import event_bp
from routes.candidate import candidate_bp
from routes.create_event import create_event_bp
from routes.manage_event import manage_event_bp
from routes.create_candidate import create_candidate_bp
from routes.manage_candidate import manage_candidate_bp

app = Flask(__name__)

# Set the secret key to a random value
app.secret_key = os.urandom(24)

# Register the blueprints
app.register_blueprint(create_candidate_bp)
app.register_blueprint(manage_candidate_bp)
app.register_blueprint(candidate_bp)
app.register_blueprint(event_bp)
app.register_blueprint(create_event_bp)
app.register_blueprint(manage_event_bp)
app.register_blueprint(index_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(liste_bp)

custom_route_names = {

    "/": "Accueil",
    "/admin": "Admin",
    "/liste": "Liste"
}

@app.context_processor
def inject_routes():
    return dict(custom_route_names=custom_route_names)

if __name__ == "__main__":
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    app.run(host="127.0.0.1", port=8080, debug=debug_mode)

@app.route('/database', methods=['GET', 'POST', 'UPDATE', 'DELETE'])
def database():
    query = []
    for i in session.query(models.BlogPost):
        query.append((i.title, i.post, i.date))
    return render_template('database.html', query = query)