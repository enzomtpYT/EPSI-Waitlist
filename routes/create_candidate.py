from flask import Blueprint, render_template, request, redirect, url_for, flash
import sqlite3
from lib.database import get_db_connection

create_candidate_bp = Blueprint('create_candidate', __name__)

@create_candidate_bp.route('/admin/create_candidate', methods=('GET', 'POST'))
def create_candidate():
    if request.method == 'POST':
        lastname = request.form['candidate_lastname']
        name = request.form['candidate_name']
        email = request.form['candidate_email']
        conn = get_db_connection()
        error = None

        if not lastname:
            error = 'Le nom de famille est obligatoire.'
        elif not name:
            error = 'Le prénom de famille est obligatoire.'
        elif not email:
            error = 'L\'adresse email est obligatoire.'

        if error is None:
            try:
                conn.execute(
                    "INSERT INTO Candidate (lastname_candidate, name_candidate, email_candidate) VALUES (?, ?, ?)",
                    (lastname, name, email),
                )
                conn.commit()
                flash("Candidat créé avec succès!", "success")
            except sqlite3.Error as e:
                flash(f"Erreur lors de la création du candidat: {e}", "danger")
            finally:
                conn.close()
        return redirect(url_for('create_candidate.create_candidate'))

    return render_template('create_candidate.html')