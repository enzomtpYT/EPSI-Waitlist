from flask import Blueprint, render_template
import sqlite3

event_bp = Blueprint('event', __name__)

@event_bp.route("/admin/event")
def event():
    return render_template('event.html')