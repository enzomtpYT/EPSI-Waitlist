from flask import Blueprint, render_template, request, redirect, url_for, flash
from lib import database

participant_bp = Blueprint('participant', __name__)

@participant_bp.route('/admin/participant', methods=('GET', 'POST'))
def participant():
    return render_template('participant.html')

@participant_bp.route("/admin/manage_participant/participant/<int:id_participant>", methods=['GET', 'POST'])
def edit_participant(id_participant):
    participant, error = database.get_participant(id_participant)
    interviews, error = database.get_participant_interviews(id_participant)
    participant_tags, error = database.get_participant_tags(id_participant)
    tags, error = database.get_all_tags()

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
            error = database.edit_participant(name, email, id_participant)
            if error is None:
                flash("Participant mis à jour avec succès!", "success")
                return redirect(url_for('participant.edit_participant', id_participant=id_participant))
            else:
                flash(f"Erreur lors de la mise à jour du participant: {error}", "danger")

    return render_template('participant.html', interviews=interviews, participant_id=id_participant, participant=participant, tags=tags, participant_tags=participant_tags)

@participant_bp.route("/admin/manage_participant/participant/<int:id_participant>/add_tag_participant", methods=['POST'])
def add_tag_participant(id_participant):
    if 'add_tag' in request.form:
        id_tag = request.form['tag']
        error = database.add_tag_to_participant(id_participant, id_tag)
        if error:
            flash(f"Erreur lors de l'ajout du tag: {error}", "danger")
        else:
            flash("Tag ajouté avec succès!", "success")
    return redirect(url_for('participant.edit_participant', id_participant=id_participant))

@participant_bp.route("/admin/manage_participant/participant/<int:id_participant>/remove_tag_participant", methods=['POST'])
def remove_tag_participant(id_participant):
    if 'remove_tag' in request.form:
        id_tag = request.form['tag']
        error = database.remove_tag_from_participant(id_participant, id_tag)
        if error:
            flash(f"Erreur lors de la suppression du tag: {error}", "danger")
        else:
            flash("Tag supprimé avec succès!", "success")

    return redirect(url_for('participant.edit_participant', id_participant=id_participant))

@participant_bp.route("/admin/manage_participant/participant/<int:id_participant>/delete", methods=['POST'])
def delete_participant(id_participant):
    database.delete_participant(id_participant)
    return redirect(url_for('manage_participant.manage_participant'))