from flask import Blueprint, render_template, g
from lib import database

liste_bp = Blueprint('liste', __name__)

@liste_bp.route("/liste")
def liste():
    todayevent, error = database.get_event()
    if error:
        message = error
        candid = None
        inter = None
    else:
        candid, error = database.get_event_candidats(todayevent)
        if not candid:
            message = "Aucun candidats trouvés"
        else:
            message = None

        inter, error = database.get_event_intervenant(todayevent)
        if not inter:
            message = "Aucun intervenants trouvés"
    
    list = {}
    
    for interv in inter:
        all, error = database.get_even_interview_candidate(todayevent, interv['id_participant'])
        if all.__len__() > 0:
            print(f'-------{interv['name_participant']}-------')
            if interv['name_participant'] not in list:
                list[interv['name_participant']] = []
            for candid in all:
                list[interv['name_participant']].append(candid)
                print(candid['name_candidate'])
    
    data = {
        "list": [list],
        "message": None,
    }
    return render_template('liste.html', datas=data)
