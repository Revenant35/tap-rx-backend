from datetime import datetime

from firebase_admin.exceptions import FirebaseError
from flask import Blueprint, request, jsonify

from src.controllers.medication_controller import (
    create_medication,
    get_medication,
    update_medication,
    delete_medication,
    get_medications,
    get_scheduled_medications_for_user,
)
from src.models.errors.invalid_request_error import InvalidRequestError
from src.models.errors.resource_not_found_error import ResourceNotFoundError
from src.routes.auth import firebase_auth_required, get_user_id
from src.utils.constants import MAX_MEDICATION_SCHEDULED_TIMES_PER_PAGE
from src.utils.validators import validate_json

medications_bp = Blueprint("medications_bp", __name__)


@medications_bp.route("/", methods=["GET"])
@firebase_auth_required
def handle_get_medications():
    """
    Retrieve a list of medications based on the user's ID
    ---
    tags:
        - medications
    parameters:
        - name: page
          in: query
          type: integer
          required: false
          description: The page number to retrieve
          default: 1
        - name: limit
          in: query
          type: integer
          required: false
          description: The number of medications to retrieve, max limit of 50
          default: 50
    responses:
        200:
            description: A list of medications and the total number of medications
            schema:
                type: object
                properties:
                    success:
                        type: boolean
                        description: The status of the response
                    message:
                        type: string
                        description: The message of the response
                    data:
                        type: array
                        description: The list of medications
                        items:
                            $ref: '#/definitions/Medication'
                    total:
                        type: integer
                        description: The total number of medications
        401:
            description: Unauthorized
        403:
            description: Forbidden
        500:
            description: Failed to fetch medications
    """
    requesting_user_id = get_user_id(request)
    if requesting_user_id is None:
        return jsonify({"success": False, "message": "User not found"}), 403

    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 50, type=int)

    try:
        (medications, total) = get_medications(requesting_user_id, page, limit)
    except (ValueError, FirebaseError):
        return (
            jsonify({"success": False, "message": "Failed to retrieve medications"}),
            500,
        )

    return (
        jsonify(
            {
                "success": True,
                "message": "Medications found",
                "data": [medication.to_dict() for medication in medications],
                "total": total,
            }
        ),
        200,
    )


@medications_bp.route("/<medication_id>", methods=["GET"])
@firebase_auth_required
def handle_get_medication(medication_id):
    """
    Retrieve a medication by ID based on the user's ID
    ---
    tags:
        - medications
    parameters:
        - name: medication_id
          in: path
          type: string
          required: true
          description: The ID of the medication
    responses:
        200:
            description: The medication
            schema:
                type: object
                properties:
                    success:
                        type: boolean
                        description: The status of the response
                    message:
                        type: string
                        description: The message of the response
                    data:
                        $ref: '#/definitions/Medication'
        401:
            description: Unauthorized
        404:
            description: Medication not found
        500:
            description: Failed to retrieve medication

    """
    requesting_user_id = get_user_id(request)
    if requesting_user_id is None:
        return jsonify({"success": False, "message": "User not found"}), 403

    try:
        medication = get_medication(requesting_user_id, medication_id)
        if medication is None:
            return jsonify({"success": False, "message": "Medication not found"}), 404
    except (ValueError, FirebaseError):
        return (
            jsonify({"success": False, "message": "Failed to retrieve medication"}),
            500,
        )

    return (
        jsonify(
            {
                "success": True,
                "message": "Medication found",
                "data": medication.to_dict(),
            }
        ),
        200,
    )


@medications_bp.route("/", methods=["POST"])
@firebase_auth_required
@validate_json("name")
def handle_create_medication():
    """
    Create a new medication
    ---
    tags:
        - medications
    parameters:
        - in: body
          name: body
          required: true
          schema:
            $ref: '#/definitions/Medication'
    responses:
        201:
            description: Medication created successfully
            schema:
                type: object
                properties:
                    success:
                        type: boolean
                        description: The status of the response
                    message:
                        type: string
                        description: The message of the response
                    data:
                        $ref: '#/definitions/Medication'
        400:
            description: Invalid request
        403:
            description: User not found
        500:
            description: Internal server error
    """
    requesting_user_id = get_user_id(request)
    if requesting_user_id is None:
        return jsonify({"success": False, "message": "User not found"}), 403

    try:
        new_medication = create_medication(requesting_user_id, request.json)
    except InvalidRequestError as ex:
        return (
            jsonify(
                {"success": False, "error": ex.message, "message": "Invalid request"}
            ),
            400,
        )
    except ResourceNotFoundError:
        return jsonify({"success": False, "message": "User not found"}), 403
    except (ValueError, TypeError, FirebaseError) as e:
        return jsonify({"success": False, "message": "Internal server error"}), 500

    return (
        jsonify(
            {
                "success": True,
                "message": "Medication created successfully",
                "data": new_medication.to_dict(),
            }
        ),
        201,
    )


@medications_bp.route("/<medication_id>", methods=["PUT"])
@firebase_auth_required
def handle_update_medication(medication_id):
    """
    Update a medication by ID based on the user's ID
    ---
    tags:
        - medications
    parameters:
        - name: medication_id
          in: path
          type: string
          required: true
          description: The ID of the medication
        - in: body
          name: body
          required: true
          schema:
              $ref: '#/definitions/Medication'
    responses:
        200:
            description: Medication updated successfully
            schema:
                type: object
                properties:
                    success:
                        type: boolean
                        description: The status of the response
                    message:
                        type: string
                        description: The message of the response
                    data:
                        $ref: '#/definitions/Medication'
        400:
            description: Invalid request
        403:
            description: User not found
        500:
            description: Failed to update medication
    """
    requesting_user_id = get_user_id(request)
    if requesting_user_id is None:
        return jsonify({"success": False, "message": "User not found"}), 403

    try:
        medication = get_medication(requesting_user_id, medication_id)
        if medication is None:
            return jsonify({"success": False, "message": "Medication not found"}), 404
    except (ValueError, FirebaseError):
        return (
            jsonify({"success": False, "message": "Failed to retrieve medication"}),
            500,
        )

    try:
        updated_medication_data = update_medication(
            requesting_user_id, medication_id, request.json
        )
    except InvalidRequestError as ex:
        return (
            jsonify(
                {"success": False, "error": ex.message, "message": "Invalid request"}
            ),
            400,
        )
    except (FirebaseError, ValueError):
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Failed to update medication",
                }
            ),
            500,
        )

    return (
        jsonify(
            {
                "success": True,
                "message": "Medication updated",
                "data": updated_medication_data,
            }
        ),
        200,
    )


@medications_bp.route("/<medication_id>", methods=["DELETE"])
@firebase_auth_required
def handle_delete_medication(medication_id):
    """
    Delete a medication by ID based on the user's ID
    ---
    tags:
        - medications
    parameters:
        - name: medication_id
          in: path
          type: string
          required: true
          description: The ID of the medication
    responses:
        200:
            description: Medication deleted successfully
            schema:
                type: object
                properties:
                    success:
                        type: boolean
                        description: The status of the response
                    message:
                        type: string
                        description: The message of the response
        403:
            description: User not found
        404:
            description: Medication not found
        500:
            description: Failed to delete medication
    """
    requesting_user_id = get_user_id(request)
    if requesting_user_id is None:
        return jsonify({"success": False, "message": "User not found"}), 403

    try:
        initial_medication = get_medication(requesting_user_id, medication_id)
    except (ValueError, FirebaseError):
        return (
            jsonify({"success": False, "message": "Failed to retrieve medication"}),
            500,
        )

    if initial_medication is None:
        return jsonify({"success": False, "message": "Medication not found"}), 404

    try:
        delete_medication(requesting_user_id, medication_id)
    except (ValueError, FirebaseError):
        return (
            jsonify({"success": False, "message": "Failed to delete medication"}),
            500,
        )

    try:
        medication = get_medication(requesting_user_id, medication_id)
    except (ValueError, FirebaseError):
        return (
            jsonify({"success": False, "message": "Failed to delete medication"}),
            500,
        )

    if medication is None:
        return (
            jsonify({"success": True, "message": "Medication deleted successfully"}),
            200,
        )
    else:
        return (
            jsonify({"success": False, "message": "Failed to delete medication"}),
            500,
        )


@medications_bp.route("/schedule/<user_id>", methods=["GET"])
@firebase_auth_required
def handle_get_scheduled_medications(user_id):
    """
    Retrieves medication events for a medication within a specified time range.
    ---
    tags:
      - medications
    parameters:
      - name: user_id
        in: path
        required: true
        description: The user's ID.
        type: string
      - name: start_at
        in: query
        required: true
        description: The start date to filter timestamps.
        type: string
        format: date-time(iso8601)
      - name: end_at
        in: query
        required: true
        description: The end date to filter events.
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
          description: Medication scheduled timestamps retrieved successfully.
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
                  type: object
                  required:
                    - timestamp
                    - medication_id
                  properties:
                    timestamp:
                      type: string
                      format: date-time(iso8601)
                      description: The timestamp of the medication's scheduled time.
                    medication_id:
                      type: string
                      description: The medication's ID.
              next_token:
                type: string
        400:
            description: Invalid request.
        404:
            description: User not found.
        500:
            description: Internal server error.
    """
    requesting_user_id = get_user_id(request)
    if requesting_user_id is None:
        raise InvalidRequestError("User ID not included in ID token.")
    if requesting_user_id != user_id:
        raise InvalidRequestError("User ID does not match ID token.")

    try:
        start_at = request.args["start_at"]
        end_at = request.args["end_at"]
    except KeyError:
        raise InvalidRequestError("Required query parameters: start_at, end_at")

    try:
        start_at_dt = datetime.fromisoformat(start_at)
        end_at_dt = datetime.fromisoformat(end_at)
    except ValueError:
        raise InvalidRequestError("Invalid date format. Please use ISO 8601 format.")

    try:
        limit = int(request.args.get("limit", MAX_MEDICATION_SCHEDULED_TIMES_PER_PAGE))
    except ValueError:
        raise InvalidRequestError("Invalid limit value. Please use an integer value.")

    if not 0 < limit <= MAX_MEDICATION_SCHEDULED_TIMES_PER_PAGE:
        raise InvalidRequestError(
            f"Invalid limit value. "
            f"Please use a positive integer value that is less than or equal to {MAX_MEDICATION_SCHEDULED_TIMES_PER_PAGE}."
        )

    timestamps, nxt_token = get_scheduled_medications_for_user(
        user_id=user_id,
        start_at=start_at_dt,
        end_at=end_at_dt,
        limit=limit,
        start_token=request.args.get("next_token"),
    )

    return jsonify({
        "success": True,
        "message": "Medication scheduled timestamps retrieved successfully",
        "data": timestamps,
        "next_token": nxt_token
    }), 200
