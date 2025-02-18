from flask import Blueprint, render_template
manage_database_bp = Blueprint('manage_database', __name__)
@manage_database_bp.route("/admin/manage_database")
def manage_database():
    return render_template('manage_database.html')