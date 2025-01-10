from flask import Blueprint, render_template, request, redirect, url_for, flash
from lib import database

create_event_bp = Blueprint('create_event', __name__)

@create_event_bp.route('/admin/create_event', methods=('GET', 'POST'))
def create_event():
    possible_tags, error = database.get_all_tags()
    if request.method == 'POST':
        name = request.form['name_event']
        date = request.form['date_event']
        tags = request.form.getlist('tags')        
        error = None

        if not name:
            error = 'Le nom est obligatoire.'
        elif not date:
            error = 'La date est obligatoire.'
            
        if error is None:
            error = database.create_event(name, date)
            if error:
                flash(f"Erreur lors de la création de l'événement: {error}", "danger")
                return redirect(url_for('create_event.create_event'))
            added_event, error = database.get_last_added_event()
            if error:
                flash(f"Erreur lors de la récupération de l'événement: {error}", "danger")
                return redirect(url_for('create_event.create_event'))
            event_id = added_event['id_event']
            for tag_id in tags:
                error = database.add_tag_to_event(event_id, tag_id)
                if error:
                    flash(f"Erreur lors de l'ajout du tag: {error}", "danger")
                    return redirect(url_for('create_event.create_event'))
            flash("Événement créé avec succès!", "success")
            return redirect(url_for('create_event.create_event'))
        else:
            flash(f"Erreur lors de la création de l'événement: {error}", "danger")
            return redirect(url_for('create_event.create_event'))

    return render_template('create_event.html', tags=possible_tags)