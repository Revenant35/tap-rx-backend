from firebase_admin import db, exceptions
from flask import Blueprint, current_app, jsonify, request

from src.database import firebase_service
from src.models.User import User
from src.routes.auth import firebase_auth_required

users_bp = Blueprint('users_bp', __name__)


@users_bp.route('/', methods=['GET'])
def get_users():
    return jsonify({"message": "Listing all users"}), 200


@users_bp.route('/<user_id>', methods=['GET', 'PUT'])
@firebase_auth_required
def get_or_update_user_route(user_id):
    db_users_ref = db.reference("/users")
    requesting_user_id = request.decoded_token['user_id']
    if user_id != requesting_user_id:
        return jsonify({"message": "Insufficient permissions"}), 403

    if request.method == 'GET':
        return jsonify({"message": f"Retrieving user {user_id}"}), 200
    elif request.method == 'PUT':
        try:
            updated_user_data = update_user(db_users_ref, user_id, request.json)
        except UserNotFoundError:
            return jsonify({"message": "User not found"}), 404
        except (ValueError, TypeError, exceptions.FirebaseError) as ex:
            return jsonify({"message": "Failed to update user"}), 500

        return jsonify({
            "message": "User updated successfully",
            "updated data": updated_user_data
        }), 200


@users_bp.route('/', methods=['POST'])
@firebase_auth_required
def create_user_route():
    db_users_ref = db.reference("/users")
    try:
        user_id = request.json["user_id"]
    except (ValueError, KeyError) as ex:
        current_app.logger.error(f"Invalid request JSON: {ex}")
        return jsonify({"message": "Invalid request"}), 400

    requesting_user_id = request.decoded_token['user_id']
    if user_id != requesting_user_id:
        return jsonify({"message": "Insufficient permissions"}), 403

    try:
        new_user = create_user(db_users_ref, user_id, request.json)
    except InvalidRequestError:
        return jsonify({"message": "Invalid request"}), 400
    except UserAlreadyExistsError:
        return jsonify({"message": "User already exists"}), 400
    except (ValueError, TypeError, exceptions.FirebaseError) as ex:
        return jsonify({"message": "Internal server error"}), 500

    return jsonify({
        "message": "User created successfully",
        "user": new_user.to_dict()
    }), 201


def create_user(db_users_ref: db.Reference, user_id: str, user_json_dict: dict) -> User:
    """
    Creates a new user in the database.

    Args:
        db_users_ref: (firebase_admin.db.Reference) Reference to the database.
        user_id: (str) Username for user.
        user_json_dict: (dict) Dictionary containing user data.

    Returns:
        User: The newly created user.

    Raises:
        InvalidRequestError: If the request is invalid.
        UserAlreadyExistsError: If the user already exists.
        ValueError, TypeError, exceptions.FirebaseError: If an error occurs while trying to store the user.
    """

    try:
        first_name = user_json_dict["first_name"]
        last_name = user_json_dict["last_name"]

        # Not required for registration
        phone = user_json_dict.get("phone", None)
    except (ValueError, KeyError) as ex:
        current_app.logger.error(f"Invalid request JSON: {ex}")
        raise InvalidRequestError

    if firebase_service.get_node(db_users_ref, user_id) is not None:
        current_app.logger.error(f"User {user_id} already exists")
        raise UserAlreadyExistsError

    new_user = User(user_id=user_id, first_name=first_name, last_name=last_name, phone=phone)

    try:
        firebase_service.add_node(db_users_ref, new_user.user_id, new_user.to_dict())
    except (ValueError, TypeError, exceptions.FirebaseError) as ex:
        current_app.logger.error(f"Failed to create user: {ex}")
        raise ex

    return new_user


def update_user(db_users_ref: db.Reference, user_id: str, user_json_dict: dict) -> dict:
    """
    Updates an existing user in the database.

    Args:
        db_users_ref: (firebase_admin.db.Reference) Reference to the database.
        user_id: (str) Username for user.
        user_json_dict: (dict) Dictionary containing user data to be updated.

    Returns:
        dict: The updated user data.

    Raises:
        UserNotFoundError: If the user is not found.
        ValueError, TypeError, exceptions.FirebaseError: If an error occurs while trying to update the user.
    """
    if firebase_service.get_node(db_users_ref, user_id) is None:
        current_app.logger.error(f"User {user_id} not found")
        raise UserNotFoundError

    updated_user_data = {
        key: user_json_dict[key] for key in ["first_name", "last_name", "phone"] if key in user_json_dict
    }
    print(updated_user_data)
    try:
        firebase_service.update_node(db_users_ref, user_id, updated_user_data)
    except (ValueError, TypeError, exceptions.FirebaseError) as ex:
        current_app.logger.error(f"Failed to update user: {ex}")
        raise ex

    return updated_user_data


class InvalidRequestError(Exception):
    def __init__(self, message="Invalid request"):
        self.message = message
        super().__init__(self.message)


class UserAlreadyExistsError(Exception):
    def __init__(self, message="User already exists"):
        self.message = message
        super().__init__(self.message)


class UserNotFoundError(Exception):
    def __init__(self, message="User not found"):
        self.message = message
        super().__init__(self.message)
