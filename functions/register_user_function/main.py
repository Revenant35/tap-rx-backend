import json
import logging
import os

import firebase_admin
import firebase_admin.exceptions
import flask
import functions_framework
from firebase_admin import db, auth
from .localpackage import register_user

FIREBASE_KEY = "FIREBASE_DATABASE_KEY"
FIREBASE_DATABASE_URL = "FIREBASE_DATABASE_URL"


@functions_framework.http
def register_user_handler(request: flask.request):
    """
    Register a new user in the Firebase Realtime Database. Uses the Firebase Admin SDK to interact with the database.
    Args:
        request (flask.request): The request object.

    Returns:
        Response that can be converted into a flask.Response object.
    """

    try:
        request_json = request.get_json(silent=True)
        user_id = request_json["user_id"]
        first_name = request_json["first_name"]
        last_name = request_json["last_name"]

        # Not required for registration
        phone = request_json.get("phone", None)
    except (ValueError, TypeError, KeyError) as ex:
        logging.error(f"Invalid request JSON: {ex}")
        return "Invalid request", 400

    try:
        firebase_key_dict = json.loads(get_env_var(FIREBASE_KEY))
    except json.JSONDecodeError as ex:
        logging.error(f"JSON decoding error when decoding the firebase key: {ex}")
        return "Internal server error", 500
    except ValueError:
        return "Internal server error", 500

    try:
        firebase_db_url = get_env_var(FIREBASE_DATABASE_URL)
    except ValueError:
        return "Internal server error", 500

    try:
        register_user.initialize_firebase_app(firebase_key_dict, firebase_db_url)
    except (ValueError, IOError):
        return "Internal server error", 500

    try:
        user = verify_firebase_id_token(request)
        requester_user_id = user['user_id']
    except ValueError:
        return "Authorization header not present", 401
    except firebase_admin.auth.InvalidIdTokenError:
        return "Invalid or expired Firebase ID token", 403

    if user_id != requester_user_id:
        return "Insufficient permissions", 403

    try:
        db_users_ref = db.reference("/users")
    except ValueError as ex:
        logging.error(f"Invalid database reference: {ex}")
        return "Internal server error", 500

    try:
        register_user.store_user(db_users_ref, user_id, first_name, last_name, phone)
    except (ValueError, TypeError, firebase_admin.exceptions.FirebaseError):
        return "Internal server error", 500
    except register_user.UserAlreadyExistsError:
        return "User already exists", 409

    return "OK", 200


def verify_firebase_id_token(request: flask.request):
    """
    Verify the Firebase ID token in the request header and return the decoded token.
    Args:
        request: flask request object.

    Returns:
        The decoded token.

    Raises:
        ValueError: If the client authorization header is not present.
        firebase_admin.exceptions.FirebaseError: If an error occurs while verifying the token.
    """
    authorization_header = request.headers.get('X-Forwarded-Authorization')
    if not authorization_header:
        logging.error("No client authorization header.")
        raise ValueError("No client authorization header.")

    id_token = authorization_header.split('Bearer ')[1]
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        logging.error(f'Error verifying Firebase ID token: {e}')
        raise firebase_admin.auth.InvalidIdTokenError(f'Error verifying Firebase ID token: {e}')


def get_env_var(env_var_name: str) -> str:
    """
    Retrieve the value of the specified environment variable.

    Parameters:
    - env_var_name (str): The name of the environment variable to retrieve.

    Returns:
    - str: The value of the environment variable.

    Raises:
    - ValueError: If the environment variable is not set or if the var parameter is None.
    """
    if not env_var_name:
        logging.error(f"The environment variable name is None")
        raise ValueError("The environment variable name is None.")

    env_var = os.environ.get(env_var_name)
    if not env_var:
        logging.error(f"The environment variable {env_var_name} is not set.")
        raise ValueError(f"The environment variable {env_var_name} is not set.")
    return env_var
