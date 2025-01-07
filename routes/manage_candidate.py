from flask import Blueprint, render_template, request, redirect, url_for, flash
import sqlite3
from lib import database
from lib.database import get_db_connection

manage_candidate_bp = Blueprint('manage_candidate', __name__)

@manage_candidate_bp.route("/admin/manage_candidate")
def manage_candidate():
    candidates, error = database.get_allcandidates()
    return render_template('manage_candidate.html', candidates=candidates)

@manage_candidate_bp.route("/admin/manage_candidate/candidate/<int:id_candidate>/delete", methods=['POST'])
def delete_candidate(id_candidate):
    delete_statement = 'DELETE FROM Candidate WHERE id_candidate = ?'

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(delete_statement, (id_candidate,))
        conn.commit()
    except sqlite3.OperationalError as e:
        print(e)
    finally:
        conn.close()

    return redirect(url_for('manage_candidate.manage_candidate'))

    # conn = get_db_connection()
    # try:
    #     conn.execute('DELETE FROM Candidate WHERE id_candidate = ?', (id_candidate))
    #     conn.commit()
    #     flash("Candidat supprimé avec succès!", "success")
    #     return redirect(url_for('manage_candidate.manage_candidate'))
    # except sqlite3.Error as e:
    #     flash(f"Erreur lors de la suppression du candidat: {e}", "danger")
    #     return f'AIE ETTEUR {e}'
    # finally:
    #     conn.close()