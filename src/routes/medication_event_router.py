from flask import Blueprint, request, jsonify

from src.controllers.medication_event_controller import create_medication_event
from src.routes.auth import firebase_auth_required, get_user_id
from src.utils.validators import validate_json

medication_events_bp = Blueprint('medication_events_bp', __name__)


@medication_events_bp.route('/<medication_id>/events/', methods=['POST'])
@firebase_auth_required
@validate_json("timestamp")
def handle_create_medication_event(medication_id):
    # will create api docs once more testing is done and more work is done on medication events.
    requesting_user_id = get_user_id(request)

    # All errors are handled by the src/models/errors/error_handlers.py flask error handlers
    new_medication_event = create_medication_event(requesting_user_id, medication_id, request.json)

    return jsonify({
        "success": True,
        "message": "Medication event created successfully",
        "data": new_medication_event.to_dict()
    }), 201
