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
from src.routes.auth import firebase_auth_required, get_user_id, verify_user

dependant_bp = Blueprint("dependant_bp", __name__)


@dependant_bp.get("/users/<user_id>/dependants")
@firebase_auth_required
def handle_get_dependants(user_id):
    """
    Retrieve a dictionary of dependants based on the user's ID
    ---
    tags:
        - dependant
    parameters:
        - in: path
          name: user_id
          required: true
          description: The ID of the user
          schema:
            type: string
    responses:
        200:
            description: The dependants
            schema:
                type: object
                properties:
                  items:
                    $ref: '#/definitions/Dependant'
        400:
            description: Bad request
        500:
            description: Internal Server Error

    """
    user_verified, error_response = verify_user(user_id, request)
    if not user_verified:
        return error_response

    try:
        dependants = get_dependants(user_id)
    except (ValueError, FirebaseError):
        return "Internal Server Error", 500
    except InvalidRequestError as ex:
        return jsonify({"error": ex.message}), 400

    return dependants, 200


@dependant_bp.get("/users/<user_id>/dependants/<dependant_id>")
@firebase_auth_required
def handle_get_dependant(user_id, dependant_id):
    """
    Retrieve a dependant based on the user's ID and the dependant's ID
    ---
    tags:
        - dependant
    parameters:
        - in: path
          name: user_id
          required: true
          description: The ID of the user
          schema:
            type: string
        - in: path
          name: dependant_id
          required: true
          description: The ID of the dependant to retrieve
          schema:
            type: string
    responses:
        200:
            description: The dependant
            schema:
                $ref: '#/definitions/Dependant'
        400:
            description: Bad request
        500:
            description: Internal Server Error
    """
    user_verified, error_response = verify_user(user_id, request)
    if not user_verified:
        return error_response

    try:
        dependant = get_dependant(user_id, dependant_id)
    except (ValueError, FirebaseError):
        return "Internal Server Error", 500
    except InvalidRequestError as ex:
        return jsonify({"error": ex.message}), 400

    if dependant is None:
        return "Not Found", 404
    else:
        return jsonify(dependant.to_dict()), 200


@dependant_bp.post("/users/<user_id>/dependants")
@firebase_auth_required
def handle_create_dependant(user_id):
    """
    Create a dependant for the user
    ---
    tags:
        - dependant
    parameters:
        - in: path
          name: user_id
          required: true
          description: The ID of the user
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
        201:
            description: The dependant was created
        400:
            description: Bad request
        500:
            description: Internal Server Error
    """
    user_verified, error_response = verify_user(user_id, request)
    if not user_verified:
        return error_response

    try:
        create_dependant(user_id, request.json)
    except ResourceNotFoundError:
        return "Not Found", 404
    except InvalidRequestError as ex:
        return jsonify({"error": ex.message}), 400
    except FirebaseError:
        return "Internal Server Error", 500

    else:
        return "Created", 201


@dependant_bp.put("/users/<user_id>/dependants/<dependant_id>")
@firebase_auth_required
def handle_update_dependant(user_id, dependant_id):
    """
    Updates a dependant based on the user's id and the dependant's id
    ---
    tags:
        - dependant
    parameters:
        - in: path
          name: user_id
          required: true
          description: The ID of the user
          schema:
              type: string
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
        204:
            description: The dependant was updated
        400:
            description: Bad request
        404:
            description: The dependant to update was not found
        500:
            description: Internal Server Error
    """
    user_verified, error_response = verify_user(user_id, request)
    if not user_verified:
        return error_response

    try:
        update_dependant(user_id, dependant_id, request.json)
    except ResourceNotFoundError:
        return "Not Found", 404
    except InvalidRequestError as ex:
        return jsonify({"error": ex.message}), 400
    except FirebaseError:
        return "Internal Server Error", 500

    return "No Content", 204


@dependant_bp.delete("/users/<user_id>/dependants/<dependant_id>")
@firebase_auth_required
def handle_delete_dependant(user_id, dependant_id):
    """
    Deletes a dependant based on the user's id and the dependant's id
    ---
    tags:
        - dependant
    parameters:
        - in: path
          name: user_id
          required: true
          description: The ID of the user
          schema:
              type: string
        - in: path
          name: dependant_id
          required: true
          description: The ID of the dependant to delete
          schema:
            type: string
    responses:
        204:
            description: The dependant was deleted
        400:
            description: Bad request
        404:
            description: The dependant to delete was not found
        500:
            description: Internal Server Error
    """
    user_verified, error_response = verify_user(user_id, request)
    if not user_verified:
        return error_response

    try:
        delete_dependant(user_id, dependant_id)
    except ResourceNotFoundError:
        return "Not Found", 404
    except InvalidRequestError as ex:
        return jsonify({"error": ex.message}), 400
    except FirebaseError:
        return "Internal Server Error", 500

    return "No Content", 204
