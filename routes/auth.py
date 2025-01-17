from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from lib import auth, database

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        vsession, error = auth.verify_login(username, password)
        if vsession:
            session['token'] = vsession['session_token']
            flash('Login successful', 'success')
            return redirect(url_for('index.index'))
        else:
            flash(f'Login failed {error}', 'error')

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

@auth_bp.route('/register/<int:id_candidate>', methods=['POST', 'GET'])
def register_candidate(id_candidate):
    if request.method == 'POST':
        password = request.form.get('password')
        if not password:
            flash('Password is required', 'error')
        error = auth.register_candidate(id_candidate, password)
        if error:
            flash(f'Registration failed: {error}', 'error')
        else:
            flash('Registration successful', 'success')
    return redirect(request.referrer)

@auth_bp.route('/register/<int:id_participant>', methods=['POST', 'GET'])
def register_participant(id_participant):
    if request.method == 'POST':
        password = request.form.get('password')
        if not password:
            flash('Password is required', 'error')
        error = auth.register_participant(id_participant, password)
        if error:
            flash(f'Registration failed: {error}', 'error')
        else:
            flash('Registration successful', 'success')
    return redirect(request.referrer)

@auth_bp.route('/register/<int:id_employee>', methods=['POST', 'GET'])
def register_employee(id_employee):
    if request.method == 'POST':
        password = request.form.get('password')
        if not password:
            flash('Password is required', 'error')
        error = auth.register_employee(id_employee, password)
        if error:
            flash(f'Registration failed: {error}', 'error')
        else:
            flash('Registration successful', 'success')
    return redirect(request.referrer)