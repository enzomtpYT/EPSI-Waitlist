from flask import Blueprint, render_template, request, redirect, url_for, flash
from lib import database

create_event_bp = Blueprint('create_event', __name__)

@create_event_bp.route('/admin/create_event', methods=('GET', 'POST'))
def create_event():
    if request.method == 'POST':
        name = request.form['name_event']
        date = request.form['date_event']
        selected_tags = request.form['selected_tags'].split(',')
        error = None

        if not name:
            error = 'Le nom est obligatoire.'
        elif not date:
            error = 'La date est obligatoire.'

        if error is None:
            event_id, error = database.create_event(name, date)
            if error is None:
                for tag_id in selected_tags:
                    database.add_tag_to_event(event_id, tag_id)
                flash("Événement créé avec succès!", "success")
                return redirect(url_for('create_event.create_event'))
            else:
                flash(f"Erreur lors de la création de l'événement: {error}", "danger")
        else:
            flash(error, "danger")

    tags, error = database.get_all_tags()
    if error:
        flash(f"Erreur lors de la récupération des tags: {error}", "danger")
        tags = []

    return render_template('create_event.html', tags=tags)