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

@api_bp.route('/api/get_list', methods=['POST'])
def get_list():
    data = request.get_json()
    if data:
        id = data.get('id')

    if request.content_type != 'application/json':
        id, error = database.get_today_events()
        if error:
            return jsonify({"error": error}), 400
    else:
        if request.content_length == 0:
            id, error = database.get_today_events()
            if error:
                return jsonify({"error": error}), 400
        else:
            data = request.get_json()
            if data.get('id'):
                id = data.get('id')
            else:
                id, error = database.get_today_events()
                if error:
                    return jsonify({"error": error}), 400
    datas, error = api.get_list(id)
    if error:
        return jsonify({"error": error}), 400
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

@api_bp.route("/api/get_participants", methods=['GET'])
def get_participants():
    datas, error = api.get_participants()
    if error:
        return jsonify({"error": error}), 400
    return jsonify(datas)

@api_bp.route("/api/get_employees", methods=['GET'])
def get_employees():
    datas, error = api.get_employees()
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
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing data"}), 400
        id_interview = data.get('id_interview')
        if not id_interview:
            return jsonify({"error": "Missing id_interview parameter"}), 400
        updated_id, error = database.start_interview(id_interview)
        if error:
            return jsonify({"error": error}), 400
        return jsonify({"interview_id": updated_id})
    except Exception as e:
        print(f"Erreur dans start_interview: {e}")
        return jsonify({"error": "Internal server error"}), 500

@api_bp.route("/api/end_interview", methods=['POST'])
def end_interview():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing data"}), 400
        interview_id = data.get('id_interview')
        if not interview_id:
            return jsonify({"error": "Missing id_interview parameter"}), 400
        error = database.end_interview(interview_id, status=True)
        if error:
            return jsonify({"error": error}), 400
        return jsonify({"success": True})
    except Exception as e:
        print(f"Erreur dans end_interview: {e}")
        return jsonify({"error": "Internal server error"}), 500