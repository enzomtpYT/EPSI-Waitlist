from flask import Blueprint, render_template
import sqlite3
from lib import database

manage_event_bp = Blueprint('manage_event', __name__)

@manage_event_bp.route("/admin/manage_event")
def manage_event():
    events, error = database.get_allevents()
    return render_template('manage_event.html', events=events, error=error)
