from flask import Blueprint, request, render_template, flash, jsonify, redirect, session, url_for
from flask_socketio import SocketIO, join_room, send
from sock import socketio
from lib import database
import time, json

liste_bp = Blueprint('liste', __name__)

def get_data(id=None, error=None):
    event, error = database.get_event(id)
    if error:
        message = error
        candid = None
        inter = None
    else:
        candid, error = database.get_event_candidates(id)
        if not candid:
            message = "Aucun candidats trouvés"
        else:
            message = None

        inter, error = database.get_event_participant(id)
        if not inter:
            message = "Aucun intervenants trouvés"

    list = {}

    if inter:
        for interv in inter:
            all, error = database.get_event_interview_candidate(id, interv['id_participant'])
            if interv['name_participant'] not in list:
                list[interv['name_participant']] = []
            for candid in all:
                list[interv['name_participant']].append(dict(candid))  # Convert Row to dict

    data = {
        "list": [list],
        "title": event['name_event'],
        "event_id": id
    }
    return data, message

def reload(id):
    js, _ = get_data(id)
    send(js, room=id, namespace='/liste/live')

@liste_bp.route("/liste")
def liste():
    today, error = database.get_today_events()
    d, mess = get_data(today, error)
    if mess:
        flash(mess)
    return render_template('liste.html', datas=d)

@liste_bp.route("/liste/<int:id>")
def liste_id(id):
    d, mess = get_data(id)
    if mess:
        flash(mess)
    return render_template('liste.html', datas=d)

@liste_bp.route("/liste/manage")
def manage_liste():
    today, error = database.get_today_events()
    d, mess = get_data(today, error)
    if mess:
        flash(mess)
    return render_template('manage_liste.html', datas=d)

@liste_bp.route("/liste/<int:id>/manage")
def manage_liste_id(id):
    d, mess = get_data(id)
    if mess:
        flash(mess)
    return render_template('manage_liste.html', datas=d)

@liste_bp.route("/remove_candidate_from_list/<int:id_interview>", methods=['POST'])
def remove_candidate_from_list(id_interview):
    id_event, error = database.get_interview(id_interview)
    error = database.delete_interview(id_interview)
    if error:
        flash(f"Erreur lors de la suppression de l'entretien: {error}", "danger")
    else:
        flash("Entretien supprimé avec succès!", "success")
    reload(id_event['id_event'])
    return redirect(request.referrer)

# rcfaife = remove_candidate_from_all_interviews_for_event
@liste_bp.route("/rcfaife/<int:id_event>/<int:id_candidate>", methods=['POST'])
def remove_candidate_from_all_interviews_for_event(id_event, id_candidate):
    error = database.remove_candidate_from_all_interviews_for_event(id_event, id_candidate)
    if error:
        flash(f"Erreur lors de la suppression du candidat: {error}", "danger")
    else:
        flash("Candidat supprimé avec succès!", "success")
    
    reload(id_event)
    return redirect(request.referrer)

@socketio.on('join', namespace='/liste/live')
def on_join(data):
    print("Joining room "+data['room'])
    join_room(data['room'])
    print("Joined room "+data['room'])
    js, _ = get_data(data['room'])
    send(js, room=data['room'], namespace='/liste/live')
    print("Sent data to room "+data['room'])

@socketio.on('reload', namespace='/liste/live')
def on_reload(data):
    print("Reloading room "+data['room'])
    js, _ = get_data(data['room'])
    send(js, room=data['room'], namespace='/liste/live')
    print("Sent data to room "+data['room'])