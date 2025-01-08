from flask import Blueprint, Response, render_template, g
from lib import database
import time, json
from flask import jsonify

liste_bp = Blueprint('liste', __name__)

def get_data():
    todayevent, error = database.get_today_events()
    if error:
        message = error
        candid = None
        inter = None
    else:
        candid, error = database.get_event_candidates(todayevent)
        if not candid:
            message = "Aucun candidats trouvés"
        else:
            message = None

        inter, error = database.get_event_participant(todayevent)
        if not inter:
            message = "Aucun intervenants trouvés"

    list = {}

    for interv in inter:
        all, error = database.get_event_interview_candidate(todayevent, interv['id_participant'])
        if interv['name_participant'] not in list:
            list[interv['name_participant']] = []
        for candid in all:
            list[interv['name_participant']].append(dict(candid))  # Convert Row to dict

    data = {
        "list": [list],
        "message": None,
    }
    return data

def refresh():
    previous_data = None
    while True:
        data = get_data()
        if data != previous_data:
            yield json.dumps(data)
            previous_data = data
        time.sleep(1)

@liste_bp.route("/liste")
def liste():
    return render_template('liste.html', datas=get_data())

@liste_bp.route("/liste/data")
def liste_data():
    data = get_data()
    return jsonify(data)

@liste_bp.route("/liste/data-live")
def live():
    return Response(refresh(), mimetype='text/event-stream')