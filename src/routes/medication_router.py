from firebase_admin import exceptions
from flask import Blueprint, request, jsonify, current_app

from src.controllers.medication_controller import create_medication
from src.routes.auth import firebase_auth_required, verify_user
from src.utils.validators import validate_json

medications_bp = Blueprint('medications_bp', __name__)


@medications_bp.route('/', methods=['POST'])
@firebase_auth_required
@validate_json("user_id", "name")
def handle_create_medication():
    user_id = request.json["user_id"]
    user_verified, error_response = verify_user(user_id, request)
    if not user_verified:
        return error_response

    try:
        new_medication = create_medication(request.json)
    except (ValueError, TypeError, exceptions.FirebaseError) as e:
        return jsonify({
            "success": False,
            "message": "Internal server error",
            "error": str(e)
        }), 500

    return jsonify({
        "success": True,
        "message": "Medication created successfully",
        "data": new_medication.to_dict()
    }), 201
