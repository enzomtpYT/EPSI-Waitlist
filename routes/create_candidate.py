from flask import Blueprint, render_template, request, redirect, url_for, flash
from lib import database

create_candidate_bp = Blueprint('create_candidate', __name__)

@create_candidate_bp.route('/admin/create_candidate', methods=('GET', 'POST'))
def create_candidate():
    possible_tags, error = database.get_all_tags()
    if request.method == 'POST':
        lastname = request.form['candidate_lastname']
        name = request.form['candidate_name']
        email = request.form['candidate_email']
        tags = request.form.getlist('tags')
        error = None

        if not lastname:
            error = 'Le nom de famille est obligatoire.'
        elif not name:
            error = 'Le prénom est obligatoire.'
        elif not email:
            error = 'L\'adresse email est obligatoire.'

        if error is None:
            error = database.create_candidate(lastname, name, email)
            if error:
                flash(f"Erreur lors de la création du candidat: {error}", "danger")
                return redirect(url_for('create_candidate.create_candidate'))
            added_candidate, error = database.get_last_added_candidate()
            if error:
                flash(f"Erreur lors de la récupération du candidat: {error}", "danger")
                return redirect(url_for('create_candidate.create_candidate'))
            candidate_id = added_candidate['id_candidate']
            for tag_id in tags:
                error = database.add_tag_to_candidate(candidate_id, tag_id)
                if error:
                    flash(f"Erreur lors de l'ajout du tag: {error}", "danger")
                    return redirect(url_for('create_candidate.create_candidate'))
            flash("Candidat créé avec succès!", "success")
            return redirect(url_for('create_candidate.create_candidate'))
        else:
            flash(f"Erreur lors de la création du candidat: {error}", "danger")
            return redirect(url_for('create_candidate.create_candidate'))

    return render_template('create_candidate.html', tags=possible_tags)