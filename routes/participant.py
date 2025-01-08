from flask import Blueprint, render_template, request, redirect, url_for, flash
import sqlite3
from lib.database import get_db_connection
from lib import database

participant_bp = Blueprint('participant', __name__)

@participant_bp.route('/admin/participant', methods=('GET', 'POST'))
def participant():
    return render_template('participant.html')

@participant_bp.route("/admin/manage_participant/participant/<int:id_participant>", methods=['GET', 'POST'])
def edit_participant(id_participant):
    conn = get_db_connection()
    participant, error = database.get_participant(id_participant)

    if request.method == 'POST':
        name = request.form['participant_name']
        email = request.form['participant_email']
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

    interviews = conn.execute('''
    SELECT Interview.id_interview, Event.name_event, Event.date_event, Candidate.lastname_candidate, Candidate.name_candidate
    FROM Interview
    JOIN Candidate ON Interview.id_candidate = Candidate.id_candidate
    JOIN Event ON Interview.id_event = Event.id_event
    WHERE Interview.id_participant = ?
    ''', (id_participant,)).fetchall()
    conn.close()
    return render_template('participant.html', interviews=interviews, participant_id=id_participant, participant=participant)

@participant_bp.route("/admin/manage_participant/participant/<int:id_participant>/delete", methods=['POST'])
def delete_participant(id_participant):
    database.delete_participant(id_participant)
    return redirect(url_for('manage_participant.manage_participant'))