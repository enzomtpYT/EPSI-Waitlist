from flask import Blueprint, redirect, render_template, url_for, flash
from lib import database

manage_event_bp = Blueprint('manage_event', __name__)

@manage_event_bp.route("/admin/manage_event")
def manage_event():
    return render_template('manage_event.html')