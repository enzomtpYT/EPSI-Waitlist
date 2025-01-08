from flask import Blueprint, render_template, request, redirect, url_for, flash
import sqlite3
from lib.database import get_db_connection

create_participant_bp = Blueprint('create_participant', __name__)

@create_participant_bp.route('/admin/create_participant', methods=('GET', 'POST'))
def create_participant():
   if request.method == 'POST':
        name = request.form['participant_name']
        email = request.form['participant_email']
        conn = get_db_connection()
        error = None

        if not name:
            error = 'Le nom est obligatoire.'
        elif not email:
            error = 'L\'adresse email est obligatoire.'

        if error is None:
            try:
                conn.execute("INSERT INTO Participant (name_participant, email_participant) VALUES (?, ?, ?)", (name, email))
                conn.commit()
                flash("Intervenant créé avec succès!", "success")
            except sqlite3.Error as e:
                flash(f"Erreur lors de la création de l'intervenant: {e}", "danger")
            finally:
                conn.close()
        return redirect(url_for('create_participant.create_participant'))

   return render_template('create_participant.html')