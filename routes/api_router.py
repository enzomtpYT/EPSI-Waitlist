from flask import Blueprint, jsonify
from lib import api

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/get_event_participants', methods=['GET'])
def manage_event_participants_api(id_event):
    datas, error = api.get_event_participants(id_event)
    return jsonify(datas)