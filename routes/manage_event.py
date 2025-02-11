from flask import Blueprint, redirect, render_template, url_for, flash
from lib import database

manage_event_bp = Blueprint('manage_event', __name__)

@manage_event_bp.route("/admin/manage_event")
def manage_event():
    events, error = database.get_all_events()
    if error:
        flash("Erreur lors de la récupération des événements", "danger")
        return render_template('manage_event.html', events=[])

    events_with_tags = []
    for event in events:
        event_dict = dict(event)
        event_tags, error = database.get_event_tags(event['id_event'])
        if error:
            flash(f"Erreur lors de la récupération des tags pour l'événement {event['name_event']}: {error}", "danger")
            event['tags'] = []
        else:
            event_dict['tags'] = event_tags
        events_with_tags.append(event_dict)

    return render_template('manage_event.html', events=events_with_tags)

@manage_event_bp.route("/admin/manage_event/<int:id_event>/delete", methods=['POST'])
def delete_event(id_event):
    error = database.delete_event(id_event)
    if error:
        flash(f"Erreur lors de la suppression de l'événement: {error}", "danger")
    return redirect(url_for('manage_event.manage_event'))