from flask import Blueprint, render_template, request, redirect, url_for, flash
from lib import database

create_event_bp = Blueprint('create_event', __name__)

@create_event_bp.route('/admin/create_event', methods=('GET', 'POST'))
def create_event():
    if request.method == 'POST':
        name = request.form['name_event']
        date = request.form['date_event']
        error = None

        if not name:
            error = 'Le nom est obligatoire.'
        elif not date:
            error = 'L\'adresse email est obligatoire.'

        if error is None:
            error = database.create_event(name, date)
            if error is None:
                flash("Événement créé avec succès!", "success")
                return redirect(url_for('create_event.create_event'))
            else:
                flash(f"Erreur lors de la création de l'Événement: {error}", "danger")
                return redirect(url_for('create_event.create_event'))

    return render_template('create_event.html')