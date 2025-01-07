from flask import Blueprint, redirect, render_template, url_for
from lib import database

manage_event_bp = Blueprint('manage_event', __name__)

@manage_event_bp.route("/admin/manage_event")
def manage_event():
    events, error = database.get_allevents()
    return render_template('manage_event.html', events=events, error=error)

@manage_event_bp.route("/admin/manage_event/<int:id_event>/delete", methods=['POST'])
def delete_event(id_event):
    error = database.delete_event(id_event)
    return redirect(url_for('manage_event.manage_event'))