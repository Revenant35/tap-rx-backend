from firebase_admin.exceptions import FirebaseError
from flask import Blueprint, request, jsonify

from src.controllers.dependant_controller import (
    get_dependants,
    get_dependant,
    create_dependant,
    update_dependant,
    delete_dependant,
)
from src.models.errors.invalid_request_error import InvalidRequestError
from src.models.errors.resource_not_found_error import ResourceNotFoundError
from src.routes.auth import firebase_auth_required, get_user_id

dependant_bp = Blueprint("dependant_bp", __name__)


@dependant_bp.get("/")
@firebase_auth_required
def handle_get_dependants():
    """
    Retrieve a list of dependants based on the user's ID
    ---
    tags:
        - dependant
    responses:
        200:
            description: A list of dependants belonging to the user
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
                        description: The list of dependants
                        items:
                            $ref: '#/definitions/Dependant'
                    total:
                        type: integer
                        description: The total number of dependants
        401:
            description: Unauthorized
        403:
            description: Forbidden
            schema:
                type: object
                properties:
                    success:
                        type: boolean
                        description: The status of the response
                        example: false
                    message:
                        type: string
                        description: The message of the response
        500:
            description: Failed to fetch dependants
            schema:
                type: object
                properties:
                    success:
                        type: boolean
                        description: The status of the response
                        example: false
                    message:
                        type: string
                        description: The message of the response
    """
    requesting_user_id = get_user_id(request)
    if requesting_user_id is None:
        return jsonify({"success": False, "message": "User not found"}), 403

    try:
        (dependants, total) = get_dependants(requesting_user_id)
    except (ValueError, FirebaseError):
        return (
            jsonify({"success": False, "message": "Failed to retrieve dependants"}),
            500,
        )
    except InvalidRequestError as ex:
        return jsonify({"success": False, "message": ex.message}), 400

    return (
        jsonify(
            {
                "success": True,
                "message": "Dependants found",
                "data": dependants,
                "total": total,
            }
        ),
        200,
    )


@dependant_bp.get("/<dependant_id>")
@firebase_auth_required
def handle_get_dependant(dependant_id):
    """
    Retrieve a dependant based on the user's ID and the dependant's ID
    ---
    tags:
        - dependant
    parameters:
        - in: path
          name: dependant_id
          required: true
          description: The ID of the dependant to retrieve
          schema:
            type: string
    responses:
        200:
            description: The dependant belonging to the user
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
                        type: object
                        description: The dependant
                        items:
                            $ref: '#/definitions/Dependant'
        401:
            description: Unauthorized
        403:
            description: Forbidden
            schema:
                type: object
                properties:
                    success:
                        type: boolean
                        description: The status of the response
                        example: false
                    message:
                        type: string
                        description: The message of the response
        500:
            description: Failed to fetch dependants
            schema:
                type: object
                properties:
                    success:
                        type: boolean
                        description: The status of the response
                        example: false
                    message:
                        type: string
                        description: The message of the response
    """
    requesting_user_id = get_user_id(request)
    if requesting_user_id is None:
        return jsonify({"success": False, "message": "User not found"}), 403

    try:
        dependant = get_dependant(requesting_user_id, dependant_id)
    except (ValueError, FirebaseError):
        return (
            jsonify({"success": False, "message": "Failed to retrieve dependant"}),
            500,
        )
    except InvalidRequestError as ex:
        return jsonify({"success": False, "message": ex.message}), 400

    if dependant is None:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Dependant not found",
                }
            ),
            404,
        )
    else:
        return (
            jsonify(
                {
                    "success": True,
                    "message": "Dependant found",
                    "data": dependant,
                }
            ),
            200,
        )


@dependant_bp.post("/")
@firebase_auth_required
def handle_create_dependant():
    """
    Create a dependant for the user
    ---
    tags:
        - dependant
    parameters:
        - in: body
          name: body
          required: true
          schema:
            type: object
            properties:
              first_name:
                type: string
                description: The first name of the dependant
              last_name:
                type: string
                description: The last name of the dependant
              phone:
                type: string
                description: The phone number of the dependant
    responses:
        201:
            description: The dependant created
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
                        type: object
                        description: The dependant
                        items:
                            $ref: '#/definitions/Dependant'
        400:
            description: Invalid request
            schema:
                type: object
                properties:
                    success:
                        type: boolean
                        description: The status of the response
                        example: false
                    message:
                        type: string
                        description: The message of the response
        401:
            description: Unauthorized
        403:
            description: Forbidden
            schema:
                type: object
                properties:
                    success:
                        type: boolean
                        description: The status of the response
                        example: false
                    message:
                        type: string
                        description: The message of the response
        500:
            description: Failed to create dependant
            schema:
                type: object
                properties:
                    success:
                        type: boolean
                        description: The status of the response
                        example: false
                    message:
                        type: string
                        description: The message of the response
    """
    requesting_user_id = get_user_id(request)
    if requesting_user_id is None:
        return jsonify({"success": False, "message": "User not found"}), 403

    try:
        new_dependant = create_dependant(requesting_user_id, request.json)
    except (InvalidRequestError, ResourceNotFoundError) as ex:
        return jsonify({"success": False, "message": ex.message}), 400
    except FirebaseError:
        return (
            jsonify({"success": False, "message": "Failed to create dependant"}),
            500,
        )

    return (
        jsonify(
            {
                "success": True,
                "message": "Dependant created",
                "data": new_dependant,
            }
        ),
        201,
    )


@dependant_bp.put("/<dependant_id>")
@firebase_auth_required
def handle_update_dependant(dependant_id):
    """
    Updates a dependant based on the user's id and the dependant's id
    ---
    tags:
        - dependant
    parameters:
        - in: path
          name: dependant_id
          required: true
          description: The ID of the dependant to update
          schema:
            type: string
        - in: body
          name: body
          required: true
          schema:
            type: object
            properties:
              first_name:
                type: string
                description: The first name of the dependant
              last_name:
                type: string
                description: The last name of the dependant
              phone:
                type: string
                description: The phone number of the dependant
    responses:
        200:
            description: The dependant updated
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
                        type: object
                        description: The dependant
                        items:
                            $ref: '#/definitions/Dependant'
        400:
            description: Invalid request
            schema:
                type: object
                properties:
                    success:
                        type: boolean
                        description: The status of the response
                        example: false
                    message:
                        type: string
                        description: The message of the response
        401:
            description: Unauthorized
        403:
            description: Forbidden
            schema:
                type: object
                properties:
                    success:
                        type: boolean
                        description: The status of the response
                        example: false
                    message:
                        type: string
                        description: The message of the response
        404:
            description: The dependant to update was not found
            schema:
                type: object
                properties:
                    success:
                        type: boolean
                        description: The status of the response
                    message:
                        type: string
                        description: The message of the response
        500:
            description: Failed to update dependant
            schema:
                type: object
                properties:
                    success:
                        type: boolean
                        description: The status of the response
                        example: false
                    message:
                        type: string
                        description: The message of the response
    """
    requesting_user_id = get_user_id(request)
    if requesting_user_id is None:
        return jsonify({"success": False, "message": "User not found"}), 403

    try:
        updated_dependant = update_dependant(
            requesting_user_id, dependant_id, request.json
        )
    except (InvalidRequestError, ResourceNotFoundError) as ex:
        return jsonify({"success": False, "message": ex.message}), 400
    except FirebaseError:
        return (
            jsonify({"success": False, "message": "Failed to update dependant"}),
            500,
        )

    if updated_dependant is None:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Dependant not found",
                }
            ),
            404,
        )
    else:
        return (
            jsonify(
                {
                    "success": True,
                    "message": "Dependant updated",
                    "data": updated_dependant,
                }
            ),
            200,
        )


@dependant_bp.delete("/<dependant_id>")
@firebase_auth_required
def handle_delete_dependant(dependant_id):
    """
    Deletes a dependant based on the user's id and the dependant's id
    ---
    tags:
        - dependant
    parameters:
        - in: path
          name: dependant_id
          required: true
          description: The ID of the dependant to delete
          schema:
            type: string
    responses:
        200:
            description: The dependant was deleted
        401:
            description: Unauthorized
        403:
            description: Forbidden
            schema:
                type: object
                properties:
                    success:
                        type: boolean
                        description: The status of the response
                        example: false
                    message:
                        type: string
                        description: The message of the response
        404:
            description: The dependant to delete was not found
            schema:
                type: object
                properties:
                    success:
                        type: boolean
                        description: The status of the response
                    message:
                        type: string
                        description: The message of the response
        500:
            description: Failed to delete dependant
            schema:
                type: object
                properties:
                    success:
                        type: boolean
                        description: The status of the response
                        example: false
                    message:
                        type: string
                        description: The message of the response
    """
    requesting_user_id = get_user_id(request)
    if requesting_user_id is None:
        return jsonify({"success": False, "message": "User not found"}), 403

    try:
        delete_dependant(requesting_user_id, dependant_id)
    except (InvalidRequestError, ResourceNotFoundError) as ex:
        return jsonify({"success": False, "message": ex.message}), 404
    except FirebaseError:
        return (
            jsonify({"success": False, "message": "Failed to delete dependant"}),
            500,
        )

    return jsonify({"success": True, "message": "Dependant deleted"}), 200
