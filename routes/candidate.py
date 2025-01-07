from flask import Blueprint, render_template, request, redirect, url_for, flash
from lib import database

candidate_bp = Blueprint('candidate', __name__)

@candidate_bp.route("/admin/candidate")
def candidate():
    return render_template('candidate.html')

@candidate_bp.route("/admin/manage_candidate/candidate/<int:id_candidate>", methods=['GET', 'POST'])
def edit_candidate(id_candidate):
    candidate, error = database.get_candidate(id_candidate)

    if request.method == 'POST':
        lastname = request.form['candidate_lastname']
        name = request.form['candidate_name']
        email = request.form['candidate_email']
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
                flash("Candidat mis à jour avec succès!", "success")
                return redirect(url_for('candidate.edit_candidate', id_candidate=id_candidate))
            else:
                flash(f"Erreur lors de la mise à jour du Candidat: {error}", "danger")
    return render_template('candidate.html', candidate=candidate)

@candidate_bp.route("/admin/manage_candidate/candidate/<int:id_candidate>/delete", methods=['POST'])
def delete_candidate(id_candidate):
    database.delete_candidate(id_candidate)
    return redirect(url_for('manage_candidate.manage_candidate'))