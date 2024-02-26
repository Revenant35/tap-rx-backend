from firebase_admin import exceptions
from flask import Blueprint, current_app, jsonify, request

from src.controllers.user_controller import get_users, update_user, create_user, get_user
from src.routes.auth import firebase_auth_required, verify_user

users_bp = Blueprint('users_bp', __name__)


@users_bp.route('/', methods=['GET'])
@firebase_auth_required
def handle_get_users():
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
    except (ValueError, TypeError, exceptions.FirebaseError) as e:
        current_app.logger.critical(f"Failed to fetch users: {e}")
        return jsonify({
            "success": False,
            "message": "Failed to fetch users",
            "error": str(e)
        }), 500


@users_bp.route('/<user_id>', methods=['GET'])
@firebase_auth_required
def handle_get_user(user_id):
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
    except (ValueError, TypeError, exceptions.FirebaseError) as e:
        current_app.logger.critical(f"Failed to fetch user: {e}")
        return jsonify({
            "success": False,
            "message": "Failed to fetch user",
            "error": str(e)
        }), 500


@users_bp.route('/', methods=['POST'])
@firebase_auth_required
def handle_create_user():

    try:
        user_id = request.json["user_id"]
    except (ValueError, KeyError) as ex:
        current_app.logger.error(f"Invalid request JSON: {ex}")
        return jsonify({
            "success": False,
            "message": "Invalid request",
            "error": "Invalid user_id"
        }), 400

    user_verified, error_response = verify_user(user_id, request)
    if not user_verified:
        return error_response

    try:
        new_user = create_user(user_id, request.json)
    except (ValueError, TypeError, exceptions.FirebaseError) as e:
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
    except (ValueError, TypeError, exceptions.FirebaseError) as e:
        return jsonify({
            "success": False,
            "message": "Failed to update user",
            "error": str(e)
        }), 500

