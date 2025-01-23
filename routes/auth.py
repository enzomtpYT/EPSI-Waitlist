from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from lib import auth

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if turnstile is correct (captcha)
        cfturnstile = request.form.get('cf-turnstile-response')
        if not auth.check_turnstile(cfturnstile):
            flash('Captcha failed', 'error')
            return redirect(url_for('auth.login'))

        # Check if credentials are correct
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

@auth_bp.route('/register/candidate/<int:id_candidate>', methods=['POST', 'GET'])
def update_candidate(id_candidate):
    if request.method == 'POST':
        password = request.form.get('password')
        if not password:
            flash('Password is required', 'error')
        error = auth.update_candidate(id_candidate, password)
        if error:
            flash(f'Registration failed: {error}', 'error')
        else:
            flash('Registration successful', 'success')
    return redirect(request.referrer)

@auth_bp.route('/register/participant/<int:id_participant>', methods=['POST', 'GET'])
def update_participant(id_participant):
    if request.method == 'POST':
        password = request.form.get('password')
        if not password:
            flash('Password is required', 'error')
        error = auth.update_participant(id_participant, password)
        if error:
            flash(f'Registration failed: {error}', 'error')
        else:
            flash('Registration successful', 'success')
    return redirect(request.referrer)

@auth_bp.route('/register/employee/<int:id_employee>', methods=['POST', 'GET'])
def update_employee(id_employee):
    if request.method == 'POST':
        password = request.form.get('password')
        if not password:
            flash('Password is required', 'error')
        error = auth.update_employee(id_employee, password)
        if error:
            flash(f'Registration failed: {error}', 'error')
        else:
            flash('Registration successful', 'success')
    return redirect(request.referrer)