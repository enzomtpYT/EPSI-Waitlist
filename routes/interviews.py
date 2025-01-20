from flask import Blueprint, jsonify, render_template, request, redirect, url_for, flash, session
from lib import database, api

interviews_bp = Blueprint('interviews', __name__)

@interviews_bp.route("/interviews")
def interviews():
    if not 'token' in session:
        return redirect(url_for('auth.login'))
    events, error = api.api_interviews(session)
    if request.method == 'POST':
        feedback = request.form.get('feedback')
        id_interview = request.form.get('id_interview')
        # check if it is candidate or participant via session his session token
        # check if interview already exists with feedback
        for event in events:
            for interview in event['interviews']:
                if interview['id_interview'] == id_interview:
                    if interview['feedback']:
                        flash("Feedback already exists for this interview", "danger")
                        return redirect(url_for('interviews.interviews'))
    return render_template('FeedbackInterviews.html', events=events)

@interviews_bp.route("/api/interviews")
def api_interviews():
    return api.api_interviews(session)