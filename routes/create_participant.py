from flask import Blueprint, render_template, request, redirect, url_for, flash
from lib import database

create_participant_bp = Blueprint('create_participant', __name__)

@create_participant_bp.route('/admin/create_participant', methods=('GET', 'POST'))
def create_participant():
   if request.method == 'POST':
        name = request.form['participant_name']
        email = request.form['participant_email']
        error = None

        if not name:
            error = 'Le nom est obligatoire.'
        elif not email:
            error = 'L\'adresse email est obligatoire.'

        if error is None:
            error = database.create_participant(name, email)
            if error is None:
                flash("Participant créé avec succès!", "success")
                return redirect(url_for('create_participant.create_participant'))
            else:
                flash(f"Erreur lors de la création du participant: {error}", "danger")
                return redirect(url_for('create_participant.create_participant'))

   return render_template('create_participant.html')