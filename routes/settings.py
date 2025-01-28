from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from lib import database, auth 

settings_bp = Blueprint('settings', __name__)

@settings_bp.route("/settings", methods=['GET', 'POST'])
def settings():
    if 'token' not in session:
        return redirect(url_for('auth.login'))
    info, error = database.get_profile_info(session['token'])
    if error:
        flash(f"Erreur lors de la récupération des informations: {error}", "danger")
        return redirect(url_for('settings.settings'))
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        newpassword = request.form['newpassword']
        passwordconfirm = request.form['confirmpassword']
        error = None

        if not auth.verify_login(info['username'], password):
            error = 'Le mot de passe actuel est incorrect.'
        elif newpassword != passwordconfirm:
            error = 'Les mots de passe ne correspondent pas.'

        if error is None:
            if newpassword:
                error = auth.update_user(newpassword, info['username'])
                if error:
                    flash(f"Erreur lors de la mise à jour du mot de passe: {error}", "danger")
                    return redirect(url_for('settings.settings'))
            error = database.update_profile_info(info['username'], username, email)            
            if error is None:
                flash("Informations mises à jour avec succès!", "success")
                return redirect(url_for('settings.settings'))
            else:
                flash(f"Erreur lors de la mise à jour des informations: {error}", "danger")
                return redirect(url_for('settings.settings'))
        else:
            flash(error, "danger")
            return redirect(url_for('settings.settings'))

    return render_template('settings.html', info=info)