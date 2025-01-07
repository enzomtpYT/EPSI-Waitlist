from flask import Blueprint, render_template, request, redirect, url_for, flash
import sqlite3
from lib.database import get_db_connection

candidate_bp = Blueprint('candidate', __name__)

@candidate_bp.route("/admin/candidate")
def candidate():
    return render_template('candidate.html')

@candidate_bp.route("/admin/manage_candidate/candidate/<int:id_candidate>", methods=['GET', 'POST'])
def edit_candidate(id_candidate):
    conn = get_db_connection()
    candidate = conn.execute('SELECT * FROM Candidate WHERE id_candidate = ?', (id_candidate,)).fetchone()

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
            try:
                conn.execute('UPDATE Candidate SET lastname_candidate = ?, name_candidate = ?, email_candidate = ? WHERE id_candidate = ?', (lastname, name, email, id_candidate))
                conn.commit()
                flash("Candidat mis à jour avec succès!", "success")
            except sqlite3.Error as e:
                flash(f"Erreur lors de la mise à jour du candidat: {e}", "danger")
            finally:
                conn.close()
            return redirect(url_for('candidate.edit_candidate', id_candidate=id_candidate))

    conn.close()
    return render_template('candidate.html', candidate=candidate)

@candidate_bp.route("/admin/manage_candidate/candidate/<int:id_candidate>/delete", methods=['POST'])
def delete_candidate(id_candidate):
    conn = get_db_connection()
    try:
        conn.execute('DELETE FROM Candidate WHERE id_candidate = ?', (id_candidate))
        conn.commit()
        flash("Candidat supprimé avec succès!", "success")
    except sqlite3.Error as e:
        flash(f"Erreur lors de la suppression du candidat: {e}", "danger")
    finally:
        conn.close()
    return redirect(url_for('manage_candidate.manage_candidate'))