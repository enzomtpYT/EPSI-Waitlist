from flask import Blueprint, render_template, request, redirect, url_for, flash
from lib import database
import sqlite3
from lib.database import get_db_connection

create_tag_bp = Blueprint('create_tag', __name__)

@create_tag_bp.route('/admin/create_tag', methods=('GET', 'POST'))
def create_tag():
    if request.method == 'POST':
        name = request.form['tag_name']
        conn = get_db_connection()
        error = None

        if not name:
            error = 'Le nom est obligatoire.'

        if error is None:
            try:
                error = database.create_tag(name)
                if error is None:
                    flash("Tag créé avec succès!", "success")
                    return redirect(url_for('create_tag.create_tag'))
                else:
                    flash(f"Erreur lors de la création du tag: {error}", "danger")
                    return redirect(url_for('create_tag.create_tag'))
            except sqlite3.Error as e:
                flash(f"Erreur lors de la création du tag: {e}", "danger")
            finally:
                conn.close()
        else:
            flash(error, "danger")


    return render_template('create_tag.html')