from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from lib import database

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check if the user is an admin
        admin, error = database.get_admin_by_email(email)
        if admin and admin['password'] == password:
            session['user_id'] = admin['id_admin']
            session['role'] = 'admin'
            return redirect(url_for('admin.dashboard'))

        # Check if the user is a participant
        participant, error = database.get_participant_by_email(email)
        if participant and participant['password'] == password:
            session['user_id'] = participant['id_participant']
            session['role'] = 'participant'
            return redirect(url_for('participant_dashboard.dashboard'))

        # Check if the user is a candidate
        candidate, error = database.get_candidate_by_email(email)
        if candidate and candidate['password'] == password:
            session['user_id'] = candidate['id_candidate']
            session['role'] = 'candidate'
            return redirect(url_for('candidate_dashboard.dashboard'))

        flash('Invalid credentials', 'danger')
        return redirect(url_for('auth.login'))

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))