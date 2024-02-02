import json
import logging
import os

import firebase_admin
import firebase_admin.exceptions
import flask
import functions_framework
from firebase_admin import credentials, db

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
        initialize_firebase_app(firebase_key_dict, firebase_db_url)
    except (ValueError, IOError):
        return "Internal server error", 500

    try:
        db_users_ref = db.reference("/users")
    except ValueError as ex:
        logging.error(f"Invalid database reference: {ex}")
        return "Internal server error", 500

    try:
        store_user(db_users_ref, username, first_name, last_name, email, phone)
    except (ValueError, TypeError, firebase_admin.exceptions.FirebaseError):
        return "Internal server error", 500

    return "OK", 200


def store_user(
        db_user_ref: db.Reference, username: str, first_name: str, last_name: str, email: str, phone: str
) -> None:
    """
    Stores user item in database. Includes empty arrays that can be filled later.

    Args:
        db_user_ref: Reference to the database.
        username: Username for user.
        first_name: first name for user.
        last_name: last name for user.
        email: email for user.
        phone: phone number for user.

    Returns:
        None

    Raises:
        ValueError: If the JSON object is None or if any parameters are None.
        TypeError: If the JSON object is not a dictionary.
        firebase_admin.exceptions.FirebaseError: If an error occurs while interacting with the database.
    """
    logging.info(f"Storing user {username} in the database")
    try:
        db_user_ref.child(username).set({
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'phone': phone,
            'medications': [],
            'dependents': [],
            'monitored_by': [],
            'monitoring': []
        })
    except ValueError as ex:
        logging.error(f"Invalid JSON object: {ex}")
        raise ex
    except TypeError as ex:
        logging.error(f"Invalid JSON object type: {ex}")
        raise ex
    except firebase_admin.exceptions.FirebaseError as ex:
        logging.error(f"Firebase error: {ex}")
        raise ex


def initialize_firebase_app(firebase_key_dict: dict, firebase_db_url: str) -> None:
    if not firebase_admin._apps:
        try:
            cred = credentials.Certificate(firebase_key_dict)
        except IOError as ex:
            logging.error(f"Failed to read the certificate: {ex}")
            raise ex
        except ValueError as ex:
            logging.error(f"Invalid certificate: {ex}")
            raise ex

        try:
            firebase_admin.initialize_app(cred, {
                "databaseURL": firebase_db_url
            })
        except ValueError as ex:
            logging.error(f"Invalid app: {ex}")
            raise ex


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
