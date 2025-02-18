from flask import Blueprint, render_template
manage_event_bp = Blueprint('manage_event', __name__)
@manage_event_bp.route("/admin/manage_event")
def manage_event():
    return render_template('manage_event.html')