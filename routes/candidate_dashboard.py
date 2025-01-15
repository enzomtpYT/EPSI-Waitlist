from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from lib import database

candidate_dashboard_bp = Blueprint('candidate_dashboard', __name__)

@candidate_dashboard_bp.route('/candidate/dashboard')
def dashboard():
    candidate_id = session.get('candidate_id')
    if not candidate_id:
        return redirect(url_for('login'))

    candidate, error = database.get_candidate(candidate_id)
    if error:
        flash(error, 'danger')
        return redirect(url_for('login'))

    events, error = database.get_candidate_events(candidate_id)
    if error:
        flash(error, 'danger')
        return redirect(url_for('login'))

    interviews, error = database.get_candidate_interviews(candidate_id)
    if error:
        flash(error, 'danger')
        return redirect(url_for('login'))

    return render_template('candidate_dashboard.html', candidate=candidate, events=events, interviews=interviews)