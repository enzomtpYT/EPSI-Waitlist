from flask import Blueprint, render_template, request, redirect, url_for, flash
from lib import database, auth

candidate_bp = Blueprint('candidate', __name__)

@candidate_bp.route("/admin/manage_candidate/candidate/<int:id_candidate>", methods=['GET', 'POST'])
def edit_candidate(id_candidate):
    candidate, error = database.get_candidate(id_candidate)
    interviews, error = database.get_candidate_interviews(id_candidate)
    candidate_tags, error = database.get_candidate_tags(id_candidate)
    user_info, error = database.get_user(candidate['id_user'])
    tags, error = database.get_all_tags()

    if request.method == 'POST':
        lastname = request.form['candidate_lastname']
        name = request.form['candidate_name']
        email = request.form['candidate_email']
        username = request.form['username']
        password = request.form['password']
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
            error = database.update_username_with_id(candidate['id_user'], username)
            if password:
                error = auth.update_user(password, username)
            if error is None:
                flash("Candidat mis à jour avec succès!", "success")
                return redirect(url_for('candidate.edit_candidate', id_candidate=id_candidate))
            else:
                flash(f"Erreur lors de la mise à jour du candidat: {error}", "danger")
                return redirect(url_for('candidate.edit_candidate', id_candidate=id_candidate))

    return render_template('candidate.html', candidate=candidate, tags=tags, interviews=interviews, candidate_tags=candidate_tags, username=user_info['username'])

@candidate_bp.route("/admin/manage_candidate/candidate/<int:id_candidate>/add_tag_candidate", methods=['POST'])
def add_tag_candidate(id_candidate):
    if 'add_tag' in request.form:
        id_tag = request.form['tag']
        error = database.add_tag_to_candidate(id_candidate, id_tag)
        if error:
            flash(f"Erreur lors de l'ajout du tag: {error}", "danger")
        else:
            flash("Tag ajouté avec succès!", "success")
    return redirect(url_for('candidate.edit_candidate', id_candidate=id_candidate))

@candidate_bp.route("/admin/manage_candidate/candidate/<int:id_candidate>/remove_tag_candidate", methods=['POST'])
def remove_tag_candidate(id_candidate):
    if 'remove_tag' in request.form:
        id_tag = request.form['tag']
        error = database.remove_tag_from_candidate(id_candidate, id_tag)
        if error:
            flash(f"Erreur lors de la suppression du tag: {error}", "danger")
        else:
            flash("Tag supprimé avec succès!", "success")

    return redirect(url_for('candidate.edit_candidate', id_candidate=id_candidate))

@candidate_bp.route("/admin/manage_candidate/candidate/<int:id_candidate>/delete", methods=['POST'])
def delete_candidate(id_candidate):
    error = database.delete_candidate(id_candidate)
    if error:
        flash(f"Erreur lors de la suppression du candidat: {error}", "danger")
        return redirect(url_for('candidate.edit_candidate', id_candidate=id_candidate))
    return redirect(url_for('manage_candidate.manage_candidate'))