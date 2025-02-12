from flask import Blueprint, render_template, request, redirect, url_for, flash
from lib import database
import json

create_event_bp = Blueprint('create_event', __name__)

@create_event_bp.route('/admin/create_event', methods=('GET', 'POST'))
def create_event():
    if request.method == 'POST':
        name = request.form['name_event']
        date = request.form['date_event']
        start_time_event = request.form.get('start_time_event') or None
        end_time_event = request.form.get('end_time_event') or None
        has_timeslots = request.form.get('has_timeslots') == 'on'
        timeslots = request.form.get('timeslots')
        if timeslots:
            timeslots = json.loads(timeslots)
        selected_tags = request.form['selected_tags'].split(',')

        error = None

        if not name:
            error = 'Le nom est obligatoire.'
        elif not date:
            error = 'La date est obligatoire.'

        tags, error = database.get_all_tags()
        if error:
            flash(f"Erreur lors de la récupération des tags: {error}", "danger")
            tags = []

        if error is None:
            event_id, error = database.create_event(name, date, has_timeslots, start_time_event, end_time_event)
            if error is None:
                # if has_timeslots:
                #     for key, timeslot in timeslots.items():
                #         start_timeslot = timeslot.get('start')
                #         end_timeslot = timeslot.get('end')
                #         nbr_spots = timeslot.get('spots')
                #         if start_timeslot and end_timeslot and nbr_spots:
                #             error = database.add_timeslot_to_event(event_id, start_timeslot, end_timeslot, nbr_spots)
                #             if error:
                #                 flash(f"Erreur lors de l'ajout des créneaux horaires: {error}", "danger")
                #                 break
                #         else:
                #             error = "Les champs des créneaux horaires ne sont pas correctement remplis."
                #             flash(f"Erreur lors de l'ajout des créneaux horaires: {error}", "danger")
                #             break
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