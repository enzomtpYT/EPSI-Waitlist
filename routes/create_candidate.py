from flask import Blueprint, render_template, request, redirect, url_for, flash
from lib import database

create_candidate_bp = Blueprint('create_candidate', __name__)

@create_candidate_bp.route('/admin/create_candidate', methods=('GET', 'POST'))
def create_candidate():
    if request.method == 'POST':
        lastname = request.form['candidate_lastname']
        name = request.form['candidate_name']
        email = request.form['candidate_email']
        selected_tags = request.form['selected_tags'].split(',')
        error = None

        if not lastname:
            error = 'Le nom de famille est obligatoire.'
        elif not name:
            error = 'Le prénom est obligatoire.'
        elif not email:
            error = 'L\'adresse email est obligatoire.'

        if error is None:
            candidate_id, error = database.create_candidate(lastname, name, email)
            if error is None:
                for tag_id in selected_tags:
                    database.add_tag_to_candidate(candidate_id, tag_id)
                flash("Candidat créé avec succès!", "success")
                return redirect(url_for('create_candidate.create_candidate'))
            else:
                flash(f"Erreur lors de la création du candidat: {error}", "danger")
        else:
            flash(error, "danger")

    tags, error = database.get_all_tags()
    if error:
        flash(f"Erreur lors de la récupération des tags: {error}", "danger")
        tags = []

    return render_template('create_candidate.html', tags=tags)