from flask import Blueprint, render_template, redirect, url_for, flash, session
from lib import database

participant_dashboard_bp = Blueprint('participant_dashboard', __name__)

@participant_dashboard_bp.route('/participant/dashboard')
def dashboard():
    if 'token' not in session:
        return redirect(url_for('auth.login'))
    session_token = session['token']

    participant_id, error = database.auth_get_type_id(session_token)
    if error:
        flash(error, 'danger')
        return redirect(url_for('auth.login'))

    usertype = database.auth_get_user_type(session_token)

    if usertype != 'participant':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('auth.login'))

    participant, error = database.get_participant(participant_id)
    if error:
        flash(error, 'danger')
        return redirect(url_for('auth.login'))

    events, error = database.get_participant_events(participant_id)
    if error:
        flash(error, 'danger')
        return redirect(url_for('auth.login'))

    interviews, error = database.get_participant_interviews(participant_id)
    if error:
        flash(error, 'danger')
        return redirect(url_for('auth.login'))

    return render_template('participant_dashboard.html', participant=participant, events=events, interviews=interviews)