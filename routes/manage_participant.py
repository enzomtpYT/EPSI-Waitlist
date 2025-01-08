from flask import Blueprint, render_template, request, redirect, url_for, flash
from lib import database

manage_participant_bp = Blueprint('manage_participant', __name__)

@manage_participant_bp.route('/admin/manage_participant', methods=('GET', 'POST'))
def manage_participant():
    participants, error = database.get_all_participants()
    if error:
        flash("Erreur lors de la récupération des participants", "danger")
    return render_template('manage_participant.html', participants=participants)

@manage_participant_bp.route("/admin/manage_participant/<int:id_participant>/delete", methods=['POST'])
def delete_participant(id_participant):
    error = database.delete_participant(id_participant)
    if error:
        flash(f"Erreur lors de la suppression du Participant: {error}", "danger")
    return redirect(url_for('manage_participant.manage_participant'))