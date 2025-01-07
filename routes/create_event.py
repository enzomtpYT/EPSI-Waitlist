from flask import Blueprint, render_template, request, redirect, url_for, flash
import sqlite3
from lib.database import get_db_connection

create_event_bp = Blueprint('create_event', __name__)

@create_event_bp.route('/admin/create_event', methods=('GET', 'POST'))
def create_event():
    if request.method == 'POST':
        name = request.form['name_event']
        date = request.form['date_event']
        conn = get_db_connection()
        error = None

        if not name:
            error = 'Le nom est obligatoire.'
        elif not date:
            error = 'L\'adresse email est obligatoire.'

        if error is None:
            try:
                conn.execute(
                    "INSERT INTO Event (name_event, date_event) VALUES (?, ?)", (name, date),
                )
                conn.commit()
                flash("L'événement a été créer avec succès!", "success")
            except sqlite3.Error as e:
                flash(f"Erreur lors de la création de l'événement: {e}", "danger")
            finally:
                conn.close()
        return redirect(url_for('create_event.create_event'))

    return render_template('create_event.html')