from flask import Blueprint, render_template, request, redirect, url_for, flash
import sqlite3
from lib.database import get_db_connection

event_bp = Blueprint('event', __name__)

@event_bp.route("/admin/event")
def event():
    return render_template('event.html')

@event_bp.route("/admin/manage_event/event/<int:id_event>", methods=['GET', 'POST'])
def edit_event(id_event):
    conn = get_db_connection()
    event = conn.execute('SELECT * FROM Event WHERE id_event = ?', (id_event,)).fetchone()

    if request.method == 'POST':
        name = request.form['name_event']
        date = request.form['date_event']
        error = None
        
        if not name:
            error = 'Le Nom est obligatoire.'
        elif not date:
            error = 'La date est obligatoire.'

        if error is None:
            try:
                conn.execute(
                    'UPDATE Event SET name_event = ?, date_event = ? WHERE id_event = ?',
                    (name, date, id_event)
                )
                conn.commit()
                flash("Évennement mis à jour avec succès!", "success")
            except sqlite3.Error as e:
                flash(f"Erreur lors de la mise à jour de l'Évennement: {e}", "danger")
            finally:
                conn.close()
            return redirect(url_for('event.edit_event', id_event=id_event))

    conn.close()
    return render_template('event.html', event=event)

@event_bp.route("/admin/manage_event/event/<int:id_event>/delete", methods=['POST'])
def delete_event(id_event):
    conn = get_db_connection()
    try:
        conn.execute('DELETE FROM Event WHERE id_event = ?', (id_event))
        conn.commit()
        flash("Évennement supprimé avec succès!", "success")
    except sqlite3.Error as e:
        flash(f"Erreur lors de la suppression de l'Évennement: {e}", "danger")
    finally:
        conn.close()
    return redirect(url_for('manage_event.manage_event'))