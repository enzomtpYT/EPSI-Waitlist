from flask import request, session, redirect, url_for
from flask_socketio import send
from sock import socketio, app
from lib import permission, database
import os, time
from routes.auth import auth_bp
from routes.api_router import api_bp
from routes.index import index_bp
from routes.admin import admin_bp
from routes.manage_employee import manage_employee_bp
from routes.list import list_bp
from routes.manage_candidate import manage_candidate_bp
from routes.manage_participant import manage_participant_bp
from routes.create_event import create_event_bp
from routes.manage_event import manage_event_bp
from routes.event import event_bp
from routes.manage_waitlist import manage_waitlist_bp
from routes.manage_tag import manage_tag_bp
from routes.participant_dashboard import participant_dashboard_bp
from routes.candidate_dashboard import candidate_dashboard_bp
from routes.interviews import interviews_bp
from routes.settings import settings_bp
from routes.manage_database import manage_database_bp

# Register the blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(api_bp)
app.register_blueprint(index_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(manage_employee_bp)
app.register_blueprint(list_bp)
app.register_blueprint(manage_candidate_bp)
app.register_blueprint(manage_participant_bp)
app.register_blueprint(create_event_bp)
app.register_blueprint(manage_event_bp)
app.register_blueprint(event_bp)
app.register_blueprint(manage_waitlist_bp)
app.register_blueprint(manage_tag_bp)
app.register_blueprint(participant_dashboard_bp)
app.register_blueprint(candidate_dashboard_bp)
app.register_blueprint(interviews_bp)
app.register_blueprint(settings_bp)
app.register_blueprint(manage_database_bp)

@app.before_request
def checkroutes():
    session_token = session.get('token')
    if session_token:
        user_role = database.get_user_role_with_token(session_token)
        if not user_role:
            # If the token is invalid, clear the session and redirect to login
            session.clear()
            return redirect(url_for('auth.login'))
    return permission.checkroutes(session)

@socketio.on('message')
def handleMessage(msg):
    print('Message: ' + msg)
    time.sleep(5)
    send(msg, broadcast=True)

@app.context_processor
def inject_routes():
    user_role = None
    permissions = None
    username = ''
    if 'token' in session:
        user_role = database.get_user_role_with_token(session['token'])
        permissions, error = database.auth_get_perms_from_session(session['token'])
        userinfo, error = database.get_profile_info(session['token'])
        username = userinfo['username']
    return dict(parameters=request.args.to_dict(), session=session, user_role=user_role, perms=permissions, username=username)

if __name__ == "__main__":
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    socketio.run(app, host="0.0.0.0", port=os.getenv('SERVER_PORT'), debug=debug_mode)