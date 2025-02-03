from flask import Blueprint, jsonify, request
from lib import api, database

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/get_event_participants/<int:id_event>', methods=['GET'])
def manage_event_participants_api(id_event):
    datas, error = api.get_event_participants(id_event)
    return jsonify(datas)

@api_bp.route('/api/get_event_participants', methods=['GET', 'POST'])
def manage_event_participants_api_args():
    id_event = None
    if request.method == 'GET':
        id_event = request.args.get('id_event')
    elif request.method == 'POST':
        data = request.get_json()
        if data:
            id_event = data.get('id_event')
        if id_event is None:
            id_event = request.form.get('id_event')
    if id_event is None:
        return jsonify({"error": "Missing id_event parameter"}), 400
    datas, error = api.get_event_participants(id_event)
    return jsonify(datas)

@api_bp.route("/api/delete/<string:type>", methods=['POST'])
def delete_api(type):
    data = request.get_json()
    if data:
        id = data.get('id')
    if id is None:
        return jsonify({"error": "Missing id parameter"}), 400
    error = None
    error = api.delete(type, id)
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"success": True})

@api_bp.route("/api/add/<string:type>", methods=['POST'])
def add_api(type):
    data = request.get_json()
    if data:
        error = api.add(type, data)
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"success": True}), 200

@api_bp.route("/api/update/<string:type>", methods=['POST'])
def update_api(type):
    data = request.get_json()
    if data:
        error = api.update(type, data)
    if error:
        return jsonify({"Erreur: ": error}), 400
    return jsonify({"success": True}), 200

@api_bp.route("/api/get_candidates", methods=['GET'])
def get_candidates():
    datas, error = api.get_candidates()
    if error:
        return jsonify({"error": error}), 400
    return jsonify(datas)

@api_bp.route("/api/get_tags", methods=['GET'])
def get_tags():
    datas, error = api.database.get_all_tags()
    if error:
        return jsonify({"error": error}), 400
    return jsonify(datas)

@api_bp.route("/api/start_interview", methods=['POST'])
def start_interview():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing data"}), 400
    id_interview = data.get('id_interview')
    if not id_interview:
        return jsonify({"error": "Missing id_interview parameter"}), 400
    updated_id, error = database.start_interview(id_interview)
    if error:
        return jsonify({"error": error}), 400
    return ({"success": True})

@api_bp.route("/api/end_interview", methods=['POST'])
def end_interview():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing data"}), 400
    id_interview = data.get('id_interview')
    if not id_interview:
        return jsonify({"error": "Missing id_interview parameter"}), 400
    error = database.end_interview(id_interview, status=True)
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"success": True})