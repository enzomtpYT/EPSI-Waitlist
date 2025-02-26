from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from lib import auth
import os

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if turnstile is correct (captcha)
        cfturnstile = request.form.get('cf-turnstile-response')
        if not auth.check_turnstile(cfturnstile):
            flash("Captcha raté", "danger")
            return redirect(url_for('auth.login'))

        # Check if credentials are correct
        vsession, error = auth.verify_login(username, password)
        if vsession:
            session['token'] = vsession
            flash("Connexion réussie", "success")
            return redirect(url_for('index.index'))
        else:
            flash(f'Impossible de se connecter: {error}', "danger")

    return render_template('login.html', CF_KEY=os.getenv('CF_KEY'))

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))