from flask import Blueprint, render_template, redirect, url_for, flash, session, request
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

    participant, error = database.get_participant(participant_id)
    if error:
        flash(error, 'danger')
        return redirect(url_for('auth.login'))

    tags, error = database.get_participant_tags(participant_id)
    if error:
        flash(error, 'danger')
        return redirect(url_for('auth.login'))

    events, error = database.get_participant_events(participant_id)
    if error:
        flash(error, 'danger')
        return redirect(url_for('auth.login'))

    return render_template('participant_dashboard.html', participant=participant, tags=tags, events=events)

@participant_dashboard_bp.route("/participant/update_info", methods=['POST'])
def update_participant_info():
    if 'token' not in session:
        return redirect(url_for('auth.login'))
    session_token = session['token']

    participant_id, error = database.auth_get_type_id(session_token)
    if error:
        flash(error, 'danger')
        return redirect(url_for('auth.login'))
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']

    error = None

    if not name:
        error = 'Le nom est obligatoire.'
    elif not email:
        error = 'L\'email est obligatoire.'

    if error is None:
        error = database.edit_participant(name, email, password, participant_id)
        if error is None:
            flash("Informations mises à jour avec succès!", "success")
            return redirect(url_for('participant.participant_dashboard'))
        else:
            flash(f"Erreur lors de la mise à jour des informations: {error}", "danger")

    return redirect(url_for('participant.participant_dashboard'))