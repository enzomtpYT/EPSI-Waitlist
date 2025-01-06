from flask import Blueprint, render_template

candidate_bp = Blueprint('candidate', __name__)

@candidate_bp.route("/admin/candidate")
def candidate():
    return render_template('candidate.html')