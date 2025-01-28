from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from lib import auth, database

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
            session['token'] = vsession
            flash('Login successful', 'success')
            return redirect(url_for('index.index'))
        else:
            flash(f'Login failed {error}', 'error')

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))