from flask import Blueprint, redirect, url_for, session
from lib import database

index_bp = Blueprint('index', __name__)

@index_bp.route("/")
def index():
    if 'token' not in session:
        return redirect(url_for('auth.login'))
    session_token = session['token']
    user_role = database.get_user_role_with_token(session_token)
    print(f"User role: {user_role}")
    if user_role == 'candidate' or user_role == 'participant':
        return redirect(url_for('dashboard.dashboard'))
    elif user_role in ['employee', 'admin', 'superadmin']:
        return redirect(url_for('admin.admin'))
    else:
        return redirect(url_for('auth.login'))