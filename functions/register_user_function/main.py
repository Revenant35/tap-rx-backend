import json
import logging
import os

import firebase_admin
import firebase_admin.exceptions
import flask
import functions_framework
from firebase_admin import db
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

    # TODO: Authenticate user with Auth0 before registering the user in the database.

    try:
        request_json = request.get_json(silent=True)
        username = request_json["username"]
        first_name = request_json["first_name"]
        last_name = request_json["last_name"]
        email = request_json["email"]
        phone = request_json["phone"]
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
        db_users_ref = db.reference("/users")
    except ValueError as ex:
        logging.error(f"Invalid database reference: {ex}")
        return "Internal server error", 500

    try:
        register_user.store_user(db_users_ref, username, first_name, last_name, email, phone)
    except (ValueError, TypeError, firebase_admin.exceptions.FirebaseError):
        return "Internal server error", 500
    except register_user.UserAlreadyExistsError:
        return "User already exists", 409

    return "OK", 200


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
