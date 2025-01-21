from flask import request, session
from flask_socketio import send
from sock import socketio, app
from lib import permission, database
import os, time
from routes.auth import auth_bp
from routes.api_router import api_bp
from routes.index import index_bp
from routes.admin import admin_bp
from routes.create_employee import create_employee_bp
from routes.manage_employee import manage_employee_bp
from routes.employee import employee_bp
from routes.list import list_bp
from routes.create_candidate import create_candidate_bp
from routes.manage_candidate import manage_candidate_bp
from routes.candidate import candidate_bp
from routes.create_participant import create_participant_bp
from routes.manage_participant import manage_participant_bp
from routes.participant import participant_bp
from routes.create_event import create_event_bp
from routes.manage_event import manage_event_bp
from routes.event import event_bp
from routes.manage_waitlist import manage_waitlist_bp
from routes.create_tag import create_tag_bp
from routes.manage_tag import manage_tag_bp
from routes.participant_dashboard import participant_dashboard_bp
from routes.candidate_dashboard import candidate_dashboard_bp
from routes.interviews import interviews_bp

# Secret key for session (temporary hard coded for development)
app.secret_key = 'TempSecretKey'

# Register the blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(api_bp)
app.register_blueprint(index_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(create_employee_bp)
app.register_blueprint(manage_employee_bp)
app.register_blueprint(employee_bp)
app.register_blueprint(list_bp)
app.register_blueprint(create_candidate_bp)
app.register_blueprint(manage_candidate_bp)
app.register_blueprint(candidate_bp)
app.register_blueprint(create_participant_bp)
app.register_blueprint(manage_participant_bp)
app.register_blueprint(participant_bp)
app.register_blueprint(create_event_bp)
app.register_blueprint(manage_event_bp)
app.register_blueprint(event_bp)
app.register_blueprint(manage_waitlist_bp)
app.register_blueprint(create_tag_bp)
app.register_blueprint(manage_tag_bp)
app.register_blueprint(participant_dashboard_bp)
app.register_blueprint(candidate_dashboard_bp)
app.register_blueprint(interviews_bp)

custom_route_names = {
    "/": "Accueil",
    "/admin": "Admin",
    "/list": "List"
}

@app.before_request
def checkroutes():
    return permission.checkroutes(session)

@socketio.on('message')
def handleMessage(msg):
    print('Message: ' + msg)
    time.sleep(5)
    send(msg, broadcast=True)

@app.context_processor
def inject_routes():
    return dict(custom_route_names=custom_route_names, parameters=request.args.to_dict(), session=session)

def inject_user_role():
    token = session.get('token')
    if token:
        role, error = database.get_user_role_with_token(token)
        if error:
            role = None
    else:
        role = None
    return dict(user_role=role)

@app.template_filter('get_user_role_with_token')
def get_user_role_with_token(token):
    role, error = database.get_user_role_with_token(token)
    if error:
        return None
    return role

if __name__ == "__main__":
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    socketio.run(app, host="127.0.0.1", port=8080, debug=debug_mode)