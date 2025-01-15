from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from lib import database

participant_dashboard_bp = Blueprint('participant_dashboard', __name__)

@participant_dashboard_bp.route('/participant/dashboard')
def dashboard():
    participant_id = session.get('participant_id')
    if not participant_id:
        return redirect(url_for('login'))

    participant, error = database.get_participant(participant_id)
    if error:
        flash(error, 'danger')
        return redirect(url_for('login'))

    events, error = database.get_participant_events(participant_id)
    if error:
        flash(error, 'danger')
        return redirect(url_for('login'))

    interviews, error = database.get_participant_interviews(participant_id)
    if error:
        flash(error, 'danger')
        return redirect(url_for('login'))

    return render_template('participant_dashboard.html', participant=participant, events=events, interviews=interviews)