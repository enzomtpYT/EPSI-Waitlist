from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from lib import database

participant_dashboard_bp = Blueprint('participant_dashboard', __name__)

@participant_dashboard_bp.route('/participant/dashboard')
def dashboard():
    user_role = database.get_user_role_with_token(session.get('token'))
    if user_role not in ['participant', 'employee', 'admin', 'superadmin']:
        flash('Access denied', 'danger')
        return redirect(url_for('auth.login'))

    participant_id = session.get('participant_id')
    if not participant_id:
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