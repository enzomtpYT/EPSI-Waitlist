from flask import Blueprint, redirect, render_template, url_for, flash
from lib import database

manage_event_bp = Blueprint('manage_event', __name__)

@manage_event_bp.route("/admin/manage_event")
def manage_event():
    events, error = database.get_all_events()
    if error:
        flash("Erreur lors de la récupération des événements", "danger")
        return render_template('manage_event.html', events=[])

    return render_template('manage_event.html', events=dict(events))

@manage_event_bp.route("/admin/manage_event/<int:id_event>/delete", methods=['POST'])
def delete_event(id_event):
    error = database.delete_event(id_event)
    if error:
        flash(f"Erreur lors de la suppression de l'événement: {error}", "danger")
    return redirect(url_for('manage_event.manage_event'))