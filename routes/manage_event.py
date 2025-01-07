from flask import Blueprint, redirect, render_template, url_for
import sqlite3
from lib import database

manage_event_bp = Blueprint('manage_event', __name__)

@manage_event_bp.route("/admin/manage_event")
def manage_event():
    events, error = database.get_allevents()
    return render_template('manage_event.html', events=events, error=error)

@manage_event_bp.route("/admin/manage_event/<int:id_event>/delete", methods=['POST'])
def delete_event(id_event):
    try:
        conn = database.get_db_connection()
        conn.execute("DELETE FROM Event WHERE id_event = ?", (id_event,))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erreur lors de la suppression de l'évenement: {e}")
    finally:
        conn.close()
    return redirect(url_for('manage_event.manage_event'))