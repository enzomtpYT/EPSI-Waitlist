from flask import Blueprint, render_template
import sqlite3

manage_candidate_bp = Blueprint('manage_candidate', __name__)

@manage_candidate_bp.route("/admin/manage_candidate")
def manage_candidate():
    return render_template('manage_candidate.html')
