from datetime import datetime

from flask import Blueprint, request, jsonify

from src.constants import MAX_MEDICATION_EVENTS_PER_PAGE
from src.controllers.medication_event_controller import (
    create_medication_event,
    get_medication_event,
    update_medication_event,
    delete_medication_event,
    get_medication_events_for_medication_controller, get_medication_events_for_user
)
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
    # TODO: add authorization for monitoring users to access their monitored users events
    requesting_user_id = get_user_id(request)
    if requesting_user_id is None:
        raise InvalidRequestError("User ID not included in authorization header.")

    try:
        medication_event = get_medication_event(requesting_user_id, medication_id, medication_event_id)
    except ValueError:
        return jsonify({
            "success": False,
            "message": "Failed to retrieve medication event",
        }), 500

    if medication_event is None:
        raise ResourceNotFoundError(f"Medication event {medication_event_id} not found")

    return jsonify({
        "success": True,
        "message": "Medication event retrieved successfully",
        "data": medication_event.to_dict()
    }), 200


@medication_events_bp.route('/<medication_id>/events', methods=['GET'])
@firebase_auth_required
def handle_get_medication_events_for_medication(medication_id):
    """
    Retrieves medication events for a medication within a specified time range.
    ---
    tags:
      - medication events
    parameters:
      - name: medication_id
        in: path
        required: true
        description: The medication's ID.
        type: string
      - name: start_at
        in: query
        required: false
        description: The start date to filter events. Will default to the beginning of time.
        type: string
        format: date-time(iso8601)
      - name: end_at
        in: query
        required: false
        description: The end date to filter events. Will default to the current time.
        type: string
        format: date-time(iso8601)
      - name: limit
        in: query
        required: false
        description: The number of events to retrieve. Will default to 250 and cap at 250.
        type: integer
      - name: start_token
        in: query
        required: false
        description: The token to start retrieving events from. Will be returned in the response if there are more events to retrieve.
        type: string
    responses:
        200:
          description: Medication events retrieved successfully.
          schema:
            type: object
            properties:
              success:
                type: boolean
              message:
                type: string
              data:
                type: array
                items:
                  $ref: '#/definitions/MedicationEvent'
              next_token:
                type: string
        400:
            description: Invalid request.
        500:
            description: Internal server error.
    """
    # TODO: add authorization for monitoring users to access their monitored users events
    requesting_user_id = get_user_id(request)
    if requesting_user_id is None:
        raise InvalidRequestError("User ID not included in authorization header.")

    try:
        start_at = datetime.fromisoformat(request.args.get("start_at")) if request.args.get("start_at") else datetime.min
        end_at = datetime.fromisoformat(request.args.get("end_at")) if request.args.get("end_at") else datetime.utcnow()
    except (ValueError, TypeError):
        raise InvalidRequestError("Invalid date format. Please use ISO 8601 format.")

    try:
        limit = int(request.args.get("limit", MAX_MEDICATION_EVENTS_PER_PAGE))
    except ValueError:
        raise InvalidRequestError("Invalid limit value. Please use an integer value.")

    if not 0 < limit <= MAX_MEDICATION_EVENTS_PER_PAGE:
        raise InvalidRequestError(
            f"Invalid limit value. "
            f"Please use a positive integer value that is less than or equal to {MAX_MEDICATION_EVENTS_PER_PAGE}."
        )

    medications, next_token = get_medication_events_for_medication_controller(
        user_id=requesting_user_id,
        medication_id=medication_id,
        start_at=start_at,
        end_at=end_at,
        limit=limit,
        start_token=request.args.get("start_token"),
    )

    return jsonify({
        "success": True,
        "message": "Medication events retrieved successfully",
        "data": [medication_event.to_dict() for medication_event in medications],
        "next_token": next_token
    }), 200


@medication_events_bp.route('/events/users/<user_id>', methods=['GET'])
@firebase_auth_required
def handle_get_medication_events_for_user(user_id):
    """
    Retrieves medication events for a user within a specified time range.
    ---
    tags:
      - medication events
    parameters:
      - name: user_id
        in: path
        required: true
        description: The user's ID.
        type: string
      - name: start_at
        in: query
        required: false
        description: The start date to filter events. Will default to the beginning of time.
        type: string
        format: date-time(iso8601)
      - name: end_at
        in: query
        required: false
        description: The end date to filter events. Will default to the current time.
        type: string
        format: date-time(iso8601)
      - name: limit
        in: query
        required: false
        description: The number of events to retrieve. Will default to 250 and cap at 250.
        type: integer
      - name: start_token
        in: query
        required: false
        description: The token to start retrieving events from. Will be returned in the response if there are more events to retrieve.
        type: string
    responses:
        200:
          description: Medication events retrieved successfully.
          schema:
            type: object
            properties:
              success:
                type: boolean
              message:
                type: string
              data:
                type: array
                items:
                  $ref: '#/definitions/MedicationEvent'
              next_token:
                type: string
        400:
            description: Invalid request.
        404:
            description: Medication event or User not found.
        500:
            description: Internal server error.
    """
    # TODO: add authorization for monitoring users to access their monitored users events
    requesting_user_id = get_user_id(request)
    if requesting_user_id is None:
        raise InvalidRequestError("User ID not included in authorization header.")
    if requesting_user_id != user_id:
        raise InvalidRequestError("User does not have access to this users medications")

    try:
        start_at = datetime.fromisoformat(request.args.get("start_at")) if request.args.get("start_at") else datetime.min
        end_at = datetime.fromisoformat(request.args.get("end_at")) if request.args.get("end_at") else datetime.utcnow()
    except (ValueError, TypeError):
        raise InvalidRequestError("Invalid date format. Please use ISO 8601 format.")

    try:
        limit = int(request.args.get("limit", MAX_MEDICATION_EVENTS_PER_PAGE))
    except ValueError:
        raise InvalidRequestError("Invalid limit value. Please use an integer value.")

    if not 0 < limit <= MAX_MEDICATION_EVENTS_PER_PAGE:
        raise InvalidRequestError(
            f"Invalid limit value. "
            f"Please use a positive integer value that is less than or equal to {MAX_MEDICATION_EVENTS_PER_PAGE}."
        )

    try:
        medication_events, next_token = get_medication_events_for_user(
            user_id=requesting_user_id,
            start_at=start_at,
            end_at=end_at,
            limit=limit,
            start_token=request.args.get("start_token"),
        )
    except ValueError:
        return jsonify({
            "success": False,
            "message": "Failed to retrieve medication events",
        }), 500

    return jsonify({
        "success": True,
        "message": "Medication events retrieved successfully",
        "data": [medication_event.to_dict() for medication_event in medication_events],
        "next_token": next_token
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
        raise InvalidRequestError("User ID not included in authorization header.")

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
        raise InvalidRequestError("User ID not included in authorization header.")

    # All defined errors are handled by the src/models/errors/error_handlers.py flask error handlers
    updated_medication_event_data = update_medication_event(
        user_id=requesting_user_id,
        medication_id=medication_id,
        medication_event_id=medication_event_id,
        medication_event_json_dict=request.json
    )
    return jsonify({
        "success": True,
        "message": "Medication event updated successfully",
        "data": updated_medication_event_data
    }), 200


@medication_events_bp.route('/<medication_id>/events/<medication_event_id>', methods=['DELETE'])
@firebase_auth_required
def handle_delete_medication_event(medication_id, medication_event_id):
    """
    Delete a medication event.
    ---
    tags:
        - medication events
    parameters:
        - name: medication_id
          in: path
          type: string
          required: true
          description: The ID of the medication the event belongs to
        - name: medication_event_id
          in: path
          type: string
          required: true
          description: The ID of the medication event to delete
    responses:
        200:
            description: Medication event deleted successfully
            schema:
                type: object
                properties:
                    success:
                        type: boolean
                        description: The status of the response
                    message:
                        type: string
                        description: The message of the response
        400:
            description: Invalid request
        404:
            description: Medication or medication event not found
        500:
            description: Failed to delete medication
    """
    requesting_user_id = get_user_id(request)
    if requesting_user_id is None:
        raise InvalidRequestError("User ID not included in authorization header.")

    delete_medication_event(requesting_user_id, medication_id, medication_event_id)
    return jsonify({
        "success": True,
        "message": "Medication event deleted successfully"
    }), 204
