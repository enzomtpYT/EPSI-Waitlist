from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from lib import database

candidate_dashboard_bp = Blueprint('candidate_dashboard', __name__)

@candidate_dashboard_bp.route('/candidate/dashboard')
def dashboard():
    if 'token' not in session:
        return redirect(url_for('auth.login'))
    session_token = session['token']
    
    candidate_id, error = database.auth_get_type_id(session_token)
    if error:
        flash(error, 'danger')
        return redirect(url_for('auth.login'))
    
    usertype = database.auth_get_user_type(session_token)
    
    if usertype != 'candidate':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('auth.login'))

    candidate, error = database.get_candidate(candidate_id)
    if error:
        flash(error, 'danger')
        return redirect(url_for('auth.login'))

    events, error = database.get_candidate_events(candidate_id)
    if error:
        flash(error, 'danger')
        return redirect(url_for('auth.login'))

    interviews, error = database.get_candidate_interviews(candidate_id)
    if error:
        flash(error, 'danger')
        return redirect(url_for('auth.login'))

    return render_template('candidate_dashboard.html', candidate=candidate, events=events, interviews=interviews)