from firebase_admin import db, exceptions
from flask import Blueprint, current_app, jsonify, request

from src.database import firebase_service
from src.models.User import User
from src.routes.auth import firebase_auth_required

users_bp = Blueprint('users_bp', __name__)


@users_bp.route('/', methods=['GET'])
def get_users():
    return jsonify({"message": "Listing all users"}), 200


@users_bp.route('/<user_id>', methods=['GET'])
@firebase_auth_required
def get_user(user_id):
    return jsonify({"message": f"Retrieving user {user_id}"}), 200


@users_bp.route('/', methods=['POST'])
@firebase_auth_required
def modify_user():
    db_users_ref = db.reference("/users")
    try:
        user_id = request.json["user_id"]
    except (ValueError, KeyError) as ex:
        current_app.logger.error(f"Invalid request JSON: {ex}")
        return jsonify({"message": "Invalid request"}), 400

    requesting_user_id = request.decoded_token['user_id']
    if user_id != requesting_user_id:
        return jsonify({"message": "Insufficient permissions"}), 403

    if firebase_service.get_node(db_users_ref, user_id) is None:
        try:
            create_user(db_users_ref, user_id, request.json)
        except InvalidRequestError:
            return jsonify({"message": "Invalid request"}), 400
        except (ValueError, TypeError, exceptions.FirebaseError) as ex:
            return jsonify({"message": "Failed to create user"}), 500

        return jsonify({"message": "User created"}), 201
    else:
        try:
            update_user(db_users_ref, user_id, request.json)
        except (ValueError, TypeError, exceptions.FirebaseError) as ex:
            return jsonify({"message": "Failed to update user"}), 500

        return jsonify({"message": "User updated"}), 200


def create_user(db_users_ref: db.Reference, user_id: str, json_dict: dict) -> None:
    """
    Creates a new user in the database.

    Args:
        db_users_ref: (firebase_admin.db.Reference) Reference to the database.
        user_id: (str) Username for user.
        json_dict: (dict) Dictionary containing user data.

    Returns:
        None

    Raises:
        InvalidRequestError: If the request is invalid.
        ValueError, TypeError, exceptions.FirebaseError: If an error occurs while trying to store the user.
    """

    try:
        first_name = json_dict["first_name"]
        last_name = json_dict["last_name"]

        # Not required for registration
        phone = json_dict.get("phone", None)
    except (ValueError, KeyError) as ex:
        current_app.logger.error(f"Invalid request JSON: {ex}")
        raise InvalidRequestError

    new_user = User(user_id=user_id, first_name=first_name, last_name=last_name, phone=phone)

    try:
        firebase_service.add_node(db_users_ref, new_user.user_id, new_user.to_dict())
    except (ValueError, TypeError, exceptions.FirebaseError) as ex:
        current_app.logger.error(f"Failed to create user: {ex}")
        raise ex


def update_user(db_users_ref: db.Reference, user_id: str, json_dict: dict) -> None:
    """
    Updates an existing user in the database.

    Args:
        db_users_ref: (firebase_admin.db.Reference) Reference to the database.
        user_id: (str) Username for user.
        json_dict: (dict) Dictionary containing user data to be updated.

    Returns:
        None

    Raises:
        ValueError, TypeError, exceptions.FirebaseError: If an error occurs while trying to update the user.
    """
    try:
        user_dict = firebase_service.get_node(db_users_ref, user_id)
    except (ValueError, exceptions.FirebaseError) as ex:
        current_app.logger.error(f"Failed to retrieve user: {ex}")
        raise ex

    updated_user = User.from_dict(user_dict)
    updated_user.first_name = json_dict.get('first_name', updated_user.first_name)
    updated_user.last_name = json_dict.get('last_name', updated_user.last_name)
    updated_user.phone = json_dict.get('phone', updated_user.phone)

    try:
        firebase_service.add_node(db_users_ref, updated_user.user_id, updated_user.to_dict())
    except (ValueError, TypeError, exceptions.FirebaseError) as ex:
        current_app.logger.error(f"Failed to update user: {ex}")
        raise ex


class InvalidRequestError(Exception):
    def __init__(self, message="Invalid request"):
        self.message = message
        super().__init__(self.message)
