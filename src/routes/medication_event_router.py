from flask import Blueprint, request, jsonify

from src.controllers.medication_event_controller import create_medication_event, get_medication_event, \
    update_medication_event
from src.models.errors.invalid_request_error import InvalidRequestError
from src.models.errors.resource_not_found_error import ResourceNotFoundError
from src.routes.auth import firebase_auth_required, get_user_id
from src.utils.validators import validate_json

medication_events_bp = Blueprint('medication_events_bp', __name__)


@medication_events_bp.route('/<medication_id>/events/<medication_event_id>', methods=['GET'])
@firebase_auth_required
def handle_get_medication_event(medication_id, medication_event_id):
    """
    Retrieves a medication event from the database.
    ---
    tags:
      - medication events
    parameters:
      - name: medication_id
        in: path
        required: true
        description: The medication's ID.
        type: string
      - name: medication_event_id
        in: path
        required: true
        description: The medication event's ID.
        type: string
    responses:
        200:
            description: Medication event retrieved successfully.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    success:
                      type: boolean
                    message:
                      type: string
                    data:
                      $ref: '#/definitions/MedicationEvent'
        400:
            description: Invalid request.
        404:
            description: Medication event or User not found.
        500:
            description: Internal server error.
    """
    requesting_user_id = get_user_id(request)
    if requesting_user_id is None:
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404

    try:
        medication_event = get_medication_event(requesting_user_id, medication_id, medication_event_id)
    except ValueError:
        return jsonify({
            "success": False,
            "message": "Failed to retrieve medication event",
        }), 500

    if medication_event is None:
        return jsonify({
            "success": False,
            "message": "Medication event not found"
        }), 404

    return jsonify({
        "success": True,
        "message": "Medication event retrieved successfully",
        "data": medication_event.to_dict()
    }), 200


@medication_events_bp.route('/<medication_id>/events/', methods=['POST'])
@firebase_auth_required
@validate_json("timestamp")
def handle_create_medication_event(medication_id):
    """
    Creates a new medication event in the database.
    ---
    tags:
      - medication events
    parameters:
        - name: medication_id
          in: path
          required: true
          description: The medication's ID.
          type: string
        - in: body
          name: body
          required: true
          properties:
            timestamp:
              type: string
              format: date-time
              required: true
            dosage:
              type: string
              required: false
    responses:
        201:
            description: Medication event created successfully.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    success:
                      type: boolean
                    message:
                      type: string
                    data:
                      $ref: '#/definitions/MedicationEvent'
        400:
            description: Invalid request.
        404:
            description: User or Medication not found.
        500:
            description: Internal server error.

    """
    requesting_user_id = get_user_id(request)
    if requesting_user_id is None:
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404

    # All errors are handled by the src/models/errors/error_handlers.py flask error handlers
    new_medication_event = create_medication_event(requesting_user_id, medication_id, request.json)

    return jsonify({
        "success": True,
        "message": "Medication event created successfully",
        "data": new_medication_event.to_dict()
    }), 201


@medication_events_bp.route('/<medication_id>/events/<medication_event_id>', methods=['PUT'])
@firebase_auth_required
def handle_update_medication_event(medication_id, medication_event_id):
    """
    Updates a medication event in the database.
    ---
    tags:
      - medication events
    parameters:
        - name: medication_id
          in: path
          required: true
          description: The medication's ID.
          type: string
        - name: medication_event_id
          in: path
          required: true
          description: The medication event's ID.
          type: string
        - in: body
          name: body
          required: true
          properties:
            timestamp:
              type: string
              format: date-time
              required: false
            dosage:
              type: string
              required: false
    responses:
        200:
            description: Medication event updated successfully.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    success:
                      type: boolean
                    message:
                      type: string
        400:
            description: Invalid request.
        404:
            description: Medication event or User not found.
        500:
            description: Internal server error.
    """
    requesting_user_id = get_user_id(request)
    if requesting_user_id is None:
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404

    try:
        medication_event = get_medication_event(requesting_user_id, medication_id, medication_event_id)
    except ValueError:
        return jsonify({
            "success": False,
            "message": "Failed to retrieve medication event",
        }), 500

    if medication_event is None:
        raise ResourceNotFoundError(
            f"Medication event {medication_event_id} does not exist for medication {medication_id}"
        )

    if medication_event.user_id != requesting_user_id:
        raise InvalidRequestError("User does not have access to this medication event")

    # All defined errors are handled by the src/models/errors/error_handlers.py flask error handlers
    update_medication_event(medication_id, medication_event_id, request.json)
    return jsonify({
        "success": True,
        "message": "Medication event updated successfully"
    }), 200

