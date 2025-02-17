from flask import Blueprint, jsonify, request
from lib import api, database

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/get_event_participants', methods=['GET', 'POST'])
def manage_event_participants_api():
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
    if error:
        return jsonify({"error": error}), 400
    return jsonify(datas)

@api_bp.route('/api/process_event_waitlist', methods=['POST'])
def process_event_waitlist():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing data"}), 400

    id_event = data.get('id_event')
    participants = data.get('participants')

    if not id_event:
        return jsonify({"error": "Missing id_event parameter"}), 400
    if not participants:
        return jsonify({"error": "Missing participants data"}), 400

    error = api.process_event_waitlist(data)
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"success": True}), 200

@api_bp.route('/api/get_events', methods=['GET'])
def get_events():
    datas, error = api.get_events()
    if error:
        return jsonify({"error": error}), 400
    return jsonify(datas)

@api_bp.route('/api/process_event_participants', methods=['POST'])
def process_event_participants():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing data"}), 400

    id_event = data.get('id_event')
    participants = data.get('participants')
    candidates = data.get('candidates')

    if not id_event:
        return jsonify({"error": "Missing id_event parameter"}), 400
    if not participants:
        return jsonify({"error": "Missing participants data"}), 400
    if not candidates:
        return jsonify({"error": "Missing candidates data"}), 400

    error = api.process_event_participants(data)
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"success": True}), 200

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

@api_bp.route('/api/import_csv', methods=['POST'])
def import_csv():
    data = request.get_json()
    if data:
        error = api.import_csv(data)
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"success": True}), 200

@api_bp.route('/api/skip_candidate', methods=['POST'])
def skip_candidate():
    data = request.get_json()
    if data:
        event_id = data.get('id_event')
        participant_name = data.get('participant_name')
    if event_id is None:
        return jsonify({"error": "ID Évenement manquant"}), 400
    if participant_name is None:
        return jsonify({"error": "Nom Participant manquant"}), 400
    error = api.skip_candidate(event_id, participant_name)
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"success": True})

@api_bp.route('/api/move_interview', methods=['POST'])
def move_interview():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing data"}), 400
    error = api.move_interview(data)
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"success": True}), 200

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

@api_bp.route("/api/download_pdf", methods=['POST'])
def download_pdf_event():
    data = request.get_json()
    
    if data and 'id_event' in data:
        try:
            pdf, error = api.generate_pdf(data['id_event'])
            if error:
                return jsonify({"error": error}), 400
            return pdf
        except Exception as e:
            print(f"Erreur dans download_pdf_event: {e}")
            return None

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
    data = request.get_json()
    if data:
        error = api.start_interview(data)
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"success": True})

@api_bp.route("/api/end_interview", methods=['POST'])
def end_interview():
    data = request.get_json()
    if data:
        error = api.end_interview(data)
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"success": True})

@api_bp.route("/api/get_archives", methods=['GET'])
def get_archives():
    archives, error = database.get_archived_schemas()
    if error:
        return jsonify({"success": False, "error": error}), 500
    return jsonify(archives)

@api_bp.route("/api/get_candidate_interviews", methods=['GET'])
def get_candidate_interviews():
    id_candidate = request.args.get('id_candidate')
    if not id_candidate:
        return jsonify({"error": "Missing id_candidate parameter"}), 400
    interviews, error = database.get_candidate_interviews(id_candidate)
    if error:
        return jsonify({"error": error}), 400
    return jsonify(interviews)