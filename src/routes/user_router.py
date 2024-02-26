from flask import Blueprint, current_app, jsonify, request

from src.controllers.user_controller import get_users, update_user, create_user, get_user
from src.routes.auth import firebase_auth_required, verify_user
from src.utils.validators import validate_json

users_bp = Blueprint('users_bp', __name__)


@users_bp.route('/', methods=['GET'])
@firebase_auth_required
def handle_get_users():
    """
    Retrieve a list of users
    ---
    tags:
        - users
    parameters:
      - name: start_at
        in: query
        type: string
        required: false
        description: UID to start at, for cursor-based pagination
      - name: limit
        in: query
        type: integer
        required: false
        description: Number of users to retrieve, max limit of 50
        default: 50
    responses:
      200:
        description: A list of users and the UID for the next page
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
              description: The list of users
              items:
                $ref: '#/definitions/User'
            next_page:
              type: string
              description: The UID for the next page
      401:
        description: Unauthorized
      500:
        description: Failed to fetch users
    """
    # Fetch query parameters for pagination
    start_at = request.args.get('start_at', None)  # UID to start at, for cursor-based pagination
    limit = min(int(request.args.get('limit', 50)), 50)  # Enforce a max limit of 50

    try:
        users, next_page = get_users(start_at, limit)
        return jsonify({
            "success": True,
            "message": "Users found",
            "data": users,
            "next_page": next_page  # UID to be used as start_at for the next page
        }), 200
    except (ValueError, TypeError) as e:
        current_app.logger.critical(f"Failed to fetch users: {e}")
        return jsonify({
            "success": False,
            "message": "Failed to fetch users",
            "error": str(e)
        }), 500


@users_bp.route('/<user_id>', methods=['GET'])
@firebase_auth_required
def handle_get_user(user_id):
    """
    Retrieve a specific user
    ---
    tags:
      - users
    parameters:
      - name: user_id
        in: path
        type: string
        required: true
        description: The UID of the user
    responses:
      200:
        description: A list of users and the UID for the next page
        schema:
          type: object
          properties:
            success:
              type: boolean
              description: The status of the response
              value: true
            message:
              type: string
              description: The message of the response
            data:
              type: dict
              description: The found user
              items:
                $ref: '#/definitions/User'
      401:
        description: Unauthorized
      404:
        description: User not found
      500:
        description: Failed to fetch user
    """
    user_verified, error_response = verify_user(user_id, request)
    if not user_verified:
        return error_response

    try:
        user = get_user(user_id)
        return jsonify({
            "success": True,
            "message": "User found",
            "data": user
        }), 200
    except (ValueError, TypeError) as e:
        current_app.logger.critical(f"Failed to fetch user: {e}")
        return jsonify({
            "success": False,
            "message": "Failed to fetch user",
            "error": str(e)
        }), 500


@users_bp.route('/', methods=['POST'])
@firebase_auth_required
@validate_json("user_id", "first_name", "last_name")
def handle_create_user():
    """
    Create a new user
    ---
    tags:
      - users
    parameters:
      - in: body
        name: body
        required: true
        schema:
         $ref: '#/definitions/User'
    responses:
      201:
        description: User created successfully
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
              type: dict
              description: The created user
              items:
                $ref: '#/definitions/User'

      400:
        description: Invalid request
      401:
        description: Unauthorized
      409:
        description: User already exists
      500:
        description: Internal server error
    """

    user_id = request.json["user_id"]
    user_verified, error_response = verify_user(user_id, request)
    if not user_verified:
        return error_response

    try:
        new_user = create_user(user_id, request.json)
    except (ValueError, TypeError) as e:
        return jsonify({
            "success": False,
            "message": "Internal server error",
            "error": str(e)
        }), 500

    return jsonify({
        "success": True,
        "message": "User created successfully",
        "data": new_user.to_dict()
    }), 201


@users_bp.route('/<user_id>', methods=['PUT'])
@firebase_auth_required
def handle_update_user(user_id):
    """
    Updates a user
    ---
    tags:
      - users
    parameters:
      - name: user_id
        in: path
        type: string
        required: true
        description: The UID of the user
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/User'
    responses:
      200:
        description: User updated successfully
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
              type: dict
              description: The updated user
              items:
                $ref: '#/definitions/User'
      400:
        description: Invalid request
      401:
        description: Unauthorized
      409:
        description: User already exists
      500:
        description: Internal server error
    """
    user_verified, error_response = verify_user(user_id, request)
    if not user_verified:
        return error_response

    try:
        updated_user_data = update_user(user_id, request.json)
        return jsonify({
            "success": True,
            "message": "User updated",
            "data": updated_user_data
        }), 200
    except (ValueError, TypeError) as e:
        return jsonify({
            "success": False,
            "message": "Failed to update user",
            "error": str(e)
        }), 500
