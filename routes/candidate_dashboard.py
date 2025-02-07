from flask import Blueprint, render_template, redirect, url_for, flash, session, request
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

    candidate, error = database.get_candidate(candidate_id)
    if error:
        flash(error, 'danger')
        return redirect(url_for('auth.login'))

    tags, error = database.get_candidate_tags(candidate_id)
    if error:
        flash(error, 'danger')
        return redirect(url_for('auth.login'))

    events, error = database.get_candidate_events(candidate_id)
    if error:
        flash(error, 'danger')
        return redirect(url_for('auth.login'))

    return render_template('candidate_dashboard.html', candidate=candidate, tags=tags, events=events)

@candidate_dashboard_bp.route("/candidate/update_info", methods=['POST'])
def update_candidate_info():
    if 'token' not in session:
        return redirect(url_for('auth.login'))
    session_token = session['token']

    candidate_id, error = database.auth_get_type_id(session_token)
    if error:
        flash(error, 'danger')
        return redirect(url_for('auth.login'))
    lastname = request.form['last_name']
    name = request.form['first_name']
    email = request.form['email']
    password = request.form['password']

    error = None

    if not lastname:
        error = 'Le nom est obligatoire.'
    elif not name:
        error = 'Le prénom est obligatoire.'
    elif not email:
        error = 'L\'email est obligatoire.'

    if error is None:
        error = database.edit_candidate(lastname, name, email, password, candidate_id)
        if error is None:
            flash("Informations mises à jour avec succès!", "success")
            return redirect(url_for('candidate.candidate_dashboard'))
        else:
            flash(f"Erreur lors de la mise à jour des informations: {error}", "danger")

    return redirect(url_for('candidate.candidate_dashboard'))