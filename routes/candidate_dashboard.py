from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from lib import database

candidate_dashboard_bp = Blueprint('candidate_dashboard', __name__)

@candidate_dashboard_bp.route('/candidate/dashboard')
def dashboard():
    user_role = database.get_user_role_with_token(session.get('token'))
    print(f"User role: {user_role}")
    if user_role not in ['candidate', 'employee', 'admin', 'superadmin']:
        flash('Access denied', 'danger')
        return redirect(url_for('auth.login'))

    candidate_id = session.get('candidate_id')
    if not candidate_id:
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