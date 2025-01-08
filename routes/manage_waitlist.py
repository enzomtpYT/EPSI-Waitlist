from flask import Blueprint, render_template, request, redirect, url_for, flash
import sqlite3
from lib.database import get_db_connection

manage_waitlist_bp = Blueprint('manage_waitlist', __name__)

@manage_waitlist_bp.route("/admin/manage_waitlist/<int:id_event>", methods=['GET', 'POST'])
def manage_waitlist(id_event):
    conn = get_db_connection()
    event = conn.execute('SELECT * FROM Event WHERE id_event = ?', (id_event,)).fetchone()
    participants = conn.execute('SELECT * FROM Participant').fetchall()
    candidates = conn.execute('SELECT * FROM Candidate').fetchall()

    if request.method == 'POST':
        id_participant = request.form['participant']
        id_candidate = request.form['candidate']
        error = None

        if not id_participant:
            error = 'Le participant est obligatoire.'
        elif not id_candidate:
            error = 'Le candidat est obligatoire.'

        if error is None:
            try:
                conn.execute(
                    'INSERT INTO Participates (id_candidate, id_event) VALUES (?, ?)',
                    (id_candidate, id_event)
                )
                conn.commit()
                flash("Candidat ajouté à la liste d'attente avec succès!", "success")
            except sqlite3.Error as e:
                flash(f"Erreur lors de l'ajout du candidat à la liste d'attente: {e}", "danger")
            finally:
                conn.close()
            return redirect(url_for('manage_waitlist.manage_waitlist', id_event=id_event))

    conn.close()
    return render_template('manage_waitlist.html', event=event, participants=participants, candidates=candidates)