from flask import Blueprint, render_template, request, redirect, url_for, flash
from lib import database
import sqlite3
from lib.database import get_db_connection, get_all_tags, add_tag_to_candidate

create_candidate_bp = Blueprint('create_candidate', __name__)

@create_candidate_bp.route('/admin/create_candidate', methods=('GET', 'POST'))
def create_candidate():
    if request.method == 'POST':
        lastname = request.form['candidate_lastname']
        name = request.form['candidate_name']
        email = request.form['candidate_email']
        tags = request.form.getlist('tags')
        conn = get_db_connection()
        error = None

        if not lastname:
            error = 'Le nom de famille est obligatoire.'
        elif not name:
            error = 'Le prénom est obligatoire.'
        elif not email:
            error = 'L\'adresse email est obligatoire.'

        if error is None:
            try:
                conn.execute("INSERT INTO Candidate (lastname_candidate, name_candidate, email_candidate) VALUES (?, ?, ?)", (lastname, name, email))
                conn.commit()
                candidate_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
                for tag_id in tags:
                    add_tag_to_candidate(candidate_id, tag_id)
                flash("Candidat créé avec succès!", "success")
                return redirect(url_for('create_candidate.create_candidate'))
            except sqlite3.Error as e:
                flash(f"Erreur lors de la création du candidat: {e}", "danger")
            finally:
                conn.close()
        else:
            flash(error, "danger")

        # if error is None:
        #     error = database.create_candidate(lastname, name, email)
        #     if error is None:
        #         flash("Candidat créé avec succès!", "success")
        #         return redirect(url_for('create_candidate.create_candidate'))
        #     else:
        #         flash(f"Erreur lors de la création du candidat: {error}", "danger")
        #         return redirect(url_for('create_candidate.create_candidate'))

    return render_template('create_candidate.html')