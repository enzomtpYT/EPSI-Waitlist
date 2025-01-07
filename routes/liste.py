from flask import Blueprint, render_template, g
from lib import database as db

liste_bp = Blueprint('liste', __name__)

@liste_bp.route("/liste")
def liste():
    todayevent, error = db.get_event()
    if error:
        message = "Erreur lors de la récupération de l'événement"
        print(error)
    if not todayevent:
        message = "Pas d'événement aujourd'hui"
        candid = None
        inter = None
    else:
        candid, error = db.get_candidats(todayevent)
        if not candid:
            message = "Aucun candidats trouvés"

        inter, error = db.get_intervenant(todayevent)
        if not inter:
            message = "Aucun intervenants trouvés"
    
    data = {
        "candidats": candid,
        "intervenants": inter,
        "message": message
    }

    print(data)
    return render_template('liste.html', datas=data)
