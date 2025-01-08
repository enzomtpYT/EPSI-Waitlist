from flask import Blueprint, render_template, request, redirect, url_for, flash
import sqlite3
from lib import database
from lib.database import get_db_connection

event_bp = Blueprint('event', __name__)

@event_bp.route("/admin/event")
def event():
    return render_template('event.html')

@event_bp.route("/admin/manage_event/event/<int:id_event>", methods=['GET', 'POST'])
def edit_event(id_event):
    event, error = database.get_event(id_event)

    if request.method == 'POST':
        name = request.form['name_event']
        date = request.form['date_event']
        year = request.form['year_event']
        error = None

        if not name:
            error = 'Le nom est obligatoire.'
        elif not date:
            error = 'La date est obligatoire.'

        if error is None:
            error = database.edit_event(name, date, year, id_event)
            if error is None:
                flash("Événement mis à jour avec succès!", "success")
                return redirect(url_for('event.edit_event', id_event=id_event))
            else:
                flash(f"Erreur lors de la mise à jour de l'Événement: {error}", "danger")
    return render_template('event.html', event=event)

@event_bp.route("/admin/manage_event/event/<int:id_event>/interviews", methods=['GET'])
def view_interviews(id_event):
    conn = get_db_connection()
    event = conn.execute('SELECT name_event FROM Event WHERE id_event = ?', (id_event,)).fetchone()
    interviews = conn.execute('''
    SELECT Interview.id_interview, Participant.name_participant, Candidate.lastname_candidate, Candidate.name_candidate, Candidate.year_candidate, Candidate.class_candidate
    FROM Interview
    JOIN Candidate ON Interview.id_candidate = Candidate.id_candidate
    JOIN Participant ON Interview.id_participant = Participant.id_participant
    JOIN Event ON Interview.id_event = Event.id_event
    WHERE Interview.id_event = ?
    ''', (id_event,)).fetchall()
    conn.close()
    return render_template('interviews.html', interviews=interviews, event_id=id_event, event=event)

@event_bp.route("/admin/manage_event/event/<int:id_event>/delete", methods=['POST'])
def delete_event(id_event):
    database.delete_event(id_event)
    return redirect(url_for('manage_event.manage_event'))