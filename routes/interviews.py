from flask import Blueprint, jsonify, render_template, request, redirect, url_for, flash, session
from lib import database, api

interviews_bp = Blueprint('interviews', __name__)

@interviews_bp.route("/interviews", methods=['GET', 'POST'])
def interviews():
    if not 'token' in session:
        return redirect(url_for('auth.login'))
    session_token = session['token']
    events, error = api.api_interviews(session_token)
    if error:
        flash('Error fetching interviews', 'danger')
        return redirect(url_for('dashboard.dashboard'))
    
    # check if it is candidate or participant via session his session token
    type = database.auth_get_user_type(session_token)
    
    if request.method == 'POST':
        feedback = request.form.get('feedback')
        id_interview = int(request.form.get('id_interview'))
        # check if interview already exists with feedback
        for event in events.values():
            for interview in event['interviews']:
                if interview['id_interview'] == id_interview:
                    error = database.update_feedback(interview['id_interview'], feedback, type)
                    if error:
                        flash('Error updating feedback', 'danger')
                    else:
                        flash('Feedback updated', "success")
                    return redirect(url_for('interviews.interviews'))
    return render_template('FeedbackInterviews.html', events=events)

@interviews_bp.route("/api/interviews")
def api_interviews():
    if 'token' not in session:
        return {"error": "Unauthorized"}, 401
    return api.api_interviews(session_token = session['token'])