from flask import Blueprint, render_template
from lib import database

list_bp = Blueprint('list', __name__)

@list_bp.route("/list")
def list():
    today, error = database.get_today_events()
    return render_template('list.html', id=today)

@list_bp.route("/list/<int:id>")
def list_id(id):
    return render_template('list.html', id=id)

@list_bp.route("/list/manage")
def manage_list():
    today, error = database.get_today_events()
    return render_template('manage_list.html', id=today)

@list_bp.route("/list/<int:id>/manage")
def manage_list_id(id):
    return render_template('manage_list.html', id=id)