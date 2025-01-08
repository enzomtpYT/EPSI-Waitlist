from flask import Blueprint, render_template, redirect, url_for, flash
from lib import database

manage_candidate_bp = Blueprint('manage_candidate', __name__)

@manage_candidate_bp.route("/admin/manage_candidate")
def manage_candidate():
    candidates, error = database.get_all_candidates()
    if error:
        flash("Erreur lors de la récupération des candidats", "danger")
    return render_template('manage_candidate.html', candidates=candidates)

@manage_candidate_bp.route("/admin/manage_candidate/<int:id_candidate>/delete", methods=['POST'])
def delete_candidate(id_candidate):
    error = database.delete_candidate(id_candidate)
    if error:
        flash(f"Erreur lors de la suppression du Candidat: {error}", "danger")
    return redirect(url_for('manage_candidate.manage_candidate'))