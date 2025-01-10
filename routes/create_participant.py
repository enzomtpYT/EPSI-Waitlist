from flask import Blueprint, render_template, request, redirect, url_for, flash
from lib import database

create_participant_bp = Blueprint('create_participant', __name__)

@create_participant_bp.route('/admin/create_participant', methods=('GET', 'POST'))
def create_participant():
   possible_tags, error = database.get_all_tags()
   if request.method == 'POST':
        name = request.form['participant_name']
        email = request.form['participant_email']
        tags = request.form.getlist('tags')
        error = None

        if not name:
            error = 'Le nom est obligatoire.'
        elif not email:
            error = 'L\'adresse email est obligatoire.'

        if error is None:
            error = database.create_participant(name, email)
            if error:
                flash(f"Erreur lors de la création du participant: {error}", "danger")
                return redirect(url_for('create_participant.create_participant'))
            added_participant, error = database.get_last_added_participant()
            if error:
                flash(f"Erreur lors de la récupération du participant: {error}", "danger")
                return redirect(url_for('create_participant.create_participant'))
            participant_id = added_participant['id_participant']
            for tag_id in tags:
                error = database.add_tag_to_participant(participant_id, tag_id)
                if error:
                    flash(f"Erreur lors de l'ajout du tag: {error}", "danger")
                    return redirect(url_for('create_participant.create_participant'))
            flash("Participant créé avec succès!", "success")
            return redirect(url_for('create_participant.create_participant'))
        else:
            flash(f"Erreur lors de la création du participant: {error}", "danger")
            return redirect(url_for('create_participant.create_participant'))

   return render_template('create_participant.html', tags=possible_tags)