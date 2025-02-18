from flask import Blueprint, render_template, redirect, url_for, session
from lib import database
dashboard_bp = Blueprint('dashboard', __name__)
@dashboard_bp.route('/dashboard')
def dashboard():
    if 'token' not in session:
        return redirect(url_for('auth.login'))
    session_token = session['token']
    type = database.auth_get_user_type(session_token)
    if type == 'candidate' or type == 'participant':
        return render_template('dashboard.html')
    elif type == 'employee':
        return redirect(url_for('admin.admin'))
    else:
        return redirect(url_for('auth.login'))