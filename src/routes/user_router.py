from typing import Optional

from firebase_admin import db, exceptions
from flask import Blueprint, current_app, jsonify, request

from src.database import firebase_service
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
def add_user():
    db_users_ref = db.reference("/users")
    try:
        user_id = request.json["user_id"]
        first_name = request.json["first_name"]
        last_name = request.json["last_name"]

        # Not required for registration
        phone = request.json.get("phone", None)
    except (ValueError, KeyError) as ex:
        current_app.logger.error(f"Invalid request JSON: {ex}")
        return jsonify({"message": "Invalid request"}), 400

    requesting_user_id = request.decoded_token['user_id']
    if user_id != requesting_user_id:
        return jsonify({"message": "Insufficient permissions"}), 403

    try:
        store_user(db_users_ref, user_id, first_name, last_name, phone)
    except (ValueError, TypeError, exceptions.FirebaseError):
        return jsonify({"message": "Internal server error"}), 500
    except UserAlreadyExistsError:
        return jsonify({"message": "User already exists"}), 400

    return jsonify({"message": "User created"}), 201


class UserAlreadyExistsError(Exception):
    def __init__(self, message="User already exists"):
        self.message = message
        super().__init__(self.message)


def store_user(
        db_user_ref: db.Reference, user_id: str, first_name: str, last_name: str, phone: Optional[str]
) -> None:
    """
    Stores user item in database. Includes empty arrays that can be filled later.

    Args:
        db_user_ref: (firebase_admin.db.Reference) Reference to the database.
        user_id: (str) Username for user.
        first_name: (str) first name for user.
        last_name: (str) last name for user.
        phone: (Optional[str]) phone number for user.

    Returns:
        None

    Raises:
        ValueError: If the JSON object is None or if any parameters are None.
        TypeError: If the JSON object is not a dictionary.
        firebase_admin.exceptions.FirebaseError: If an error occurs while interacting with the database.
    """

    if firebase_service.get_node(db_user_ref, user_id) is not None:
        current_app.logger.error(f"User {user_id} already exists in the database")
        raise UserAlreadyExistsError

    try:
        user_data = {
            'first_name': first_name,
            'last_name': last_name,
            'medications': [],
            'dependents': [],
            'monitored_by': [],
            'monitoring': []
        }
        if phone:
            user_data['phone'] = phone
        db_user_ref.child(user_id).set(user_data)
    except ValueError as ex:
        current_app.logger.error(f"Invalid JSON object: {ex}")
        raise ex
    except TypeError as ex:
        current_app.logger.error(f"Invalid JSON object type: {ex}")
        raise ex
    except exceptions.FirebaseError as ex:
        current_app.logger.error(f"Firebase error: {ex}")
        raise ex
