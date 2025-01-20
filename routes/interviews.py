from flask import Blueprint, jsonify, render_template, request, redirect, url_for, flash, session
from lib import database, api

interviews_bp = Blueprint('interviews', __name__)

@interviews_bp.route("/interviews")
def interviews():
    events, error = api.api_interviews(session)
    print(events)
    return render_template('FeedbackInterviews.html', events=events)

@interviews_bp.route("/api/interviews")
def api_interviews():
    return api.api_interviews(session)