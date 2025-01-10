from flask import Blueprint, render_template, redirect, url_for, flash
from lib import database

manage_candidate_bp = Blueprint('manage_candidate', __name__)

@manage_candidate_bp.route("/admin/manage_candidate")
def manage_candidate():
    candidates, error = database.get_all_candidates()
    if error:
        flash("Erreur lors de la récupération des candidats", "danger")

    candidates_with_tags = []
    for candidate in candidates:
        candidate_dict = dict(candidate)
        candidate_tags, error = database.get_candidate_tags(candidate['id_candidate'])
        if error:
            flash(f"Erreur lors de la récupération des tags pour l'événement {candidate['name_candidate']}: {error}", "danger")
            candidate['tags'] = []
        else:
            candidate_dict['tags'] = candidate_tags
        candidates_with_tags.append(candidate_dict)

    return render_template('manage_candidate.html', candidates=candidates_with_tags)

@manage_candidate_bp.route("/admin/manage_candidate/<int:id_candidate>/delete", methods=['POST'])
def delete_candidate(id_candidate):
    error = database.delete_candidate(id_candidate)
    if error:
        flash(f"Erreur lors de la suppression du candidat: {error}", "danger")
    return redirect(url_for('manage_candidate.manage_candidate'))