from flask import Blueprint, current_app, jsonify, request

from src.controllers.user_controller import get_users, update_user, create_user, get_user, delete_user
from src.models.errors.invalid_request_error import InvalidRequestError
from src.routes.auth import firebase_auth_required, verify_user, get_user_id
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
      - name: page
        in: query
        type: integer
        required: false
        description: Page number
        default: 1
      - name: page_size
        in: query
        type: integer
        required: false
        description: Number of users per page
        default: 50
      - name: name
        in: query
        type: string
        required: false
        description: Filter users by name
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
    page = request.args.get('page', 1)  # Page number
    page_size = request.args.get('page_size', 50)  # Number of users per page
    name = request.args.get('name', None)  # Filter users by name

    # Check that page and page_size are integers
    try:
        page = int(page)
        page_size = int(page_size)
    except ValueError:
        return jsonify({
            "success": False,
            "message": "Invalid query parameters",
            "error": "Page and page_size must be integers"
        }), 400

    if page < 1 or page_size < 1:
        return jsonify({
            "success": False,
            "message": "Invalid query parameters",
            "error": "Page and page_size must be greater than 0"
        }), 400

    offset = (page - 1) * page_size
    limit = page_size

    try:
        users, total = get_users(offset, limit, name)
        return jsonify({
            "success": True,
            "message": "Users found",
            "data": users,
            "total": total
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


@users_bp.route('/<user_id>', methods=['DELETE'])
@firebase_auth_required
def handle_delete_user(user_id):
    requesting_user_id = get_user_id(request)
    if requesting_user_id != user_id:
        raise InvalidRequestError("User ID does not match the authorized user's ID")

    try:
        delete_user(requesting_user_id)
    except ValueError as ex:
        current_app.logger.error(f"Error while trying to delete user {user_id}: {ex}")
        return jsonify({
            "success": False,
            "message": "Failed to delete user",
        }), 500

    return jsonify({
        "success": True,
        "message": "User deleted successfully",
    }), 200

