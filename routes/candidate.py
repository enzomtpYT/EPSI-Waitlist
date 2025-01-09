from flask import Blueprint, render_template, request, redirect, url_for, flash
from lib import database
from lib.database import get_db_connection, get_all_tags, get_candidate_tags, add_tag_to_candidate, remove_tag_from_candidate, get_candidate_interviews

candidate_bp = Blueprint('candidate', __name__)

@candidate_bp.route("/admin/candidate")
def candidate():
    return render_template('candidate.html')

@candidate_bp.route("/admin/manage_candidate/candidate/<int:id_candidate>", methods=['GET', 'POST'])
def edit_candidate(id_candidate):
    conn = get_db_connection()
    candidate, error = database.get_candidate(id_candidate)
    interviews, error = database.get_candidate_interviews(id_candidate)

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
            error = database.edit_candidate(lastname, name, email, id_candidate)
            if error is None:
                # Update tags
                if tags:
                    current_tags, error = database.get_candidate_tags(id_candidate)
                    current_tag_ids = [tag['id_tag'] for tag in current_tags]

                # Add new tags
                if tags:
                    for tag_id in tags:
                        if int(tag_id) not in current_tag_ids:
                            database.add_tag_to_candidate(id_candidate, tag_id)

                # Remove old tags
                if current_tag_ids:
                    for tag_id in current_tag_ids:
                        if str(tag_id) not in tags:
                            database.remove_tag_from_candidate(id_candidate, tag_id)

                flash("Candidat mis à jour avec succès!", "success")
                return redirect(url_for('candidate.edit_candidate_route', id_candidate=id_candidate))
            else:
                flash(f"Erreur lors de la mise à jour du candidat: {error}", "danger")
                return redirect(url_for('candidate.edit_candidate_route', id_candidate=id_candidate))

    tags, error = database.get_all_tags()
    candidate_tags, error = database.get_candidate_tags(id_candidate)
    candidate_tag_ids = [tag['id_tag'] for tag in candidate_tags]
    interviews, error = database.get_candidate_interviews(id_candidate)
    return render_template('candidate.html', candidate=candidate, tags=tags, candidate_tag_ids=candidate_tag_ids, interviews=interviews)

@candidate_bp.route("/admin/manage_candidate/candidate/<int:id_candidate>/delete", methods=['POST'])
def delete_candidate(id_candidate):
    database.delete_candidate(id_candidate)
    return redirect(url_for('manage_candidate.manage_candidate'))