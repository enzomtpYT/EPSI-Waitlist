from flask import Blueprint, render_template, redirect, url_for, flash, session
from lib import database

settings_bp = Blueprint('settings', __name__)

@settings_bp.route("/settings", methods=['GET', 'POST'])
def settings():
    if 'token' not in session:
        return redirect(url_for('auth.login'))
    info, error = database.get_profile_info(session['token'])
    if error:
        flash(f"Erreur lors de la récupération des informations: {error}", "danger")
        return redirect(url_for('settings.settings'))
    


    return render_template('settings.html', info=info)