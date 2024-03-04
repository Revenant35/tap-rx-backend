from firebase_admin.exceptions import FirebaseError
from flask import Blueprint, request, jsonify

from src.controllers.medication_controller import create_medication, get_medication, update_medication, \
    delete_medication
from src.models.errors.invalid_request_error import InvalidRequestError
from src.models.errors.resource_not_found_error import ResourceNotFoundError
from src.routes.auth import firebase_auth_required, verify_user
from src.utils.validators import validate_json

medications_bp = Blueprint('medications_bp', __name__)


@medications_bp.route('/<medication_id>', methods=['GET'])
@firebase_auth_required
def handle_get_medication(medication_id):
    try:
        medication = get_medication(medication_id)
    except ResourceNotFoundError:
        return jsonify({
            "success": False,
            "message": "Medication not found"
        }), 404
    except FirebaseError:
        return jsonify({
            "success": False,
            "message": "Failed to retrieve medication"
        }), 500

    user_verified, error_response = verify_user(medication.user_id, request)
    if not user_verified:
        return error_response

    return jsonify({
        "success": True,
        "message": "Medication found",
        "data": medication.to_dict()
    }), 200


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
    except (ValueError, TypeError) as e:
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


@medications_bp.route('/<medication_id>', methods=['PUT'])
@firebase_auth_required
def handle_update_medication(medication_id):
    medication = get_medication(medication_id)
    user_verified, error_response = verify_user(medication.user_id, request)
    if not user_verified:
        return error_response

    try:
        updated_medication_data = update_medication(medication_id, request.json)
        return jsonify({
            "success": True,
            "message": "Medication updated",
            "data": updated_medication_data
        }), 200
    except InvalidRequestError as ex:
        return jsonify({
            "success": False,
            "error": ex.message,
            "message": "Invalid request"
        }), 400
    except (FirebaseError, ValueError, TypeError):
        return jsonify({
            "success": False,
            "message": "Failed to update medication",
        }), 500


@medications_bp.route('/<medication_id>', methods=['DELETE'])
@firebase_auth_required
def handle_delete_medication(medication_id):
    medication = get_medication(medication_id)
    user_verified, error_response = verify_user(medication.user_id, request)
    if not user_verified:
        return error_response

    try:
        delete_medication(medication_id)
        return jsonify({
            "success": True,
            "message": "Medication deleted"
        }), 200
    except FirebaseError:
        return jsonify({
            "success": False,
            "message": "Failed to delete medication"
        }), 500
