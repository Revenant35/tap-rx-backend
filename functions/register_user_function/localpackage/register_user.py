import logging

import firebase_admin
import firebase_admin.exceptions
from firebase_admin import db, credentials
from typing import Optional


class UserAlreadyExistsError(Exception):
    def __init__(self, message="User already exists"):
        self.message = message
        super().__init__(self.message)


def check_user_exists(db_user_ref: db.Reference, user_id: str) -> bool:
    """
    Checks if a user exists in the database.

    Args:
        db_user_ref: Reference to the database.
        user_id: Username for user.

    Returns:
        bool: True if the user exists, False otherwise.

    Raises:
        ValueError: If the username is None.
        firebase_admin.exceptions.FirebaseError: If an error occurs while interacting with the database.
    """
    if not user_id:
        logging.error(f"The username is None")
        raise ValueError("The username is None.")

    try:
        user = db_user_ref.child(user_id).get()
    except firebase_admin.exceptions.FirebaseError as ex:
        logging.error(f"Firebase error while trying to query for the username {user_id}: {ex}")
        raise ex

    return user is not None


def store_user(
        db_user_ref: db.Reference, user_id: str, first_name: str, last_name: str, phone: Optional[str]
) -> None:
    """
    Stores user item in database. Includes empty arrays that can be filled later.

    Args:
        db_user_ref: Reference to the database.
        user_id: Username for user.
        first_name: first name for user.
        last_name: last name for user.
        phone: phone number for user. Can be None.

    Returns:
        None

    Raises:
        ValueError: If the JSON object is None or if any parameters are None.
        TypeError: If the JSON object is not a dictionary.
        firebase_admin.exceptions.FirebaseError: If an error occurs while interacting with the database.
    """

    if check_user_exists(db_user_ref, user_id):
        logging.error(f"User {user_id} already exists in the database")
        raise UserAlreadyExistsError

    logging.info(f"Storing user {user_id} in the database")
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
