from flask import Blueprint, render_template

create_candidate_bp = Blueprint('create_candidate', __name__)

@create_candidate_bp.route("/admin/create_candidate")
def create_candidate():
    return render_template('create_candidate.html')