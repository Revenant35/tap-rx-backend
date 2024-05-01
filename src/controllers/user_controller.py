from firebase_admin import db, exceptions
from flask import current_app

from src.models.User import User
from src.models.errors.invalid_request_error import InvalidRequestError
from src.models.errors.resource_already_exists_error import ResourceAlreadyExistsError
from src.models.errors.resource_not_found_error import ResourceNotFoundError


def get_users(offset=0, limit=50, name=None):
    """
    Fetches a list of users from the database.
    Args:
        start_at: (int) Offset to start at, for cursor-based pagination
        limit: (int) Maximum number of users to fetch
        name: (str) Filter users by name

    Returns:
        tuple: The list of users & the total number of users.

    Raises:
        ValueError, TypeError, exceptions.FirebaseError: If an error occurs while trying to fetch the users.
    """
    # Fetch all users
    users = list(db.reference("/users").order_by_key().get().items())

    # Filter users by name
    if name:
        users = [user for user in users if name.lower() in user[1]["first_name"].lower() or name.lower() in user[1]["last_name"].lower()]

    # Determine the total number of users
    total_users = len(users)

    # Paginate the results
    users = users[offset:offset + limit]

    return users, total_users


def get_user(user_id) -> dict:
    """
    Fetches a user from the database.
    Args:
        user_id: (str) Username for user.

    Returns:
        The user's data.

    Raises:
        ResourceNotFoundError: If the user is not found.
        ValueError, TypeError, exceptions.FirebaseError: If an error occurs while trying to fetch the user.
    """

    user_data = db.reference(f"/users/{user_id}").get()
    if user_data is None:
        raise ResourceNotFoundError(f"User {user_id} does not exist")
    return user_data


def create_user(user_id: str, user_json_dict: dict) -> User:
    """
    Creates a new user in the database.

    Args:
        user_id: (str) UID for the user.
        user_json_dict: (dict) Dictionary containing user data.

    Returns:
        User: The newly created user.

    Raises:
        InvalidRequestError: If the request is invalid.
        ResourceAlreadyExistsError: If the user already exists.
        ValueError, TypeError: If an error occurs while trying to store the user.
        exceptions.FirebaseError: If an error occurs while interacting with the database.
    """

    try:
        user_data = db.reference(f"/users/{user_id}").get()
    except exceptions.FirebaseError as ex:
        current_app.logger.error(f"Firebase failure while trying to retrieve user {user_id}: {ex}")
        raise ex

    if user_data is not None:
        current_app.logger.error(f"User {user_id} already exists")
        raise ResourceAlreadyExistsError(f"User {user_id} already exists")

    try:
        first_name = user_json_dict["first_name"]
        last_name = user_json_dict["last_name"]
        phone = user_json_dict.get("phone", None)
        medications = user_json_dict.get("medications", {})
        dependents = user_json_dict.get("dependents", [])
        monitoring_users = user_json_dict.get("monitoring_users", [])
        monitored_by_users = user_json_dict.get("monitored_by_users", [])
    except (ValueError, KeyError, TypeError) as ex:
        current_app.logger.error(f"Invalid request JSON: {ex}")
        raise InvalidRequestError

    new_user = User(
        user_id=user_id,
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        medications=medications,
        dependents=dependents,
        monitoring_users=monitoring_users,
        monitored_by_users=monitored_by_users
    )

    try:
        db.reference(f"/users/{user_id}").set(new_user.to_dict())
    except (ValueError, TypeError) as ex:
        current_app.logger.error(f"Error while trying to store user {user_id}: {ex}")
        raise ex
    except exceptions.FirebaseError as ex:
        current_app.logger.error(f"Firebase failure while trying to store user {user_id}: {ex}")
        raise ex

    return new_user


def update_user(user_id: str, user_json_dict: dict) -> dict:
    """
    Updates an existing user in the database.

    Args:
        user_id: (str) Username for user.
        user_json_dict: (dict) Dictionary containing user data to be updated.

    Returns:
        dict: The user data that was updated.

    Raises:
        ResourceNotFoundError: If the user is not found.
        ValueError, TypeError: If an error occurs while trying to update the user.
        exceptions.FirebaseError: If an error occurs while interacting with the database.
    """
    try:
        user_data = db.reference(f"/users/{user_id}").get()
    except exceptions.FirebaseError as ex:
        current_app.logger.error(f"Firebase failure while trying to retrieve user {user_id}: {ex}")
        raise ex

    if user_data is None:
        current_app.logger.error(f"User {user_id} does not exist")
        raise ResourceNotFoundError(f"User {user_id} does not exist")

    updated_user_data = {}
    keys_to_copy = [
        "first_name", "last_name", "phone", "medications", "dependents", "monitoring_users", "monitored_by_users"
    ]
    for key in keys_to_copy:
        value = user_json_dict.get(key)
        if value is not None:
            updated_user_data[key] = value
    if not updated_user_data:
        raise InvalidRequestError("No valid fields to update")

    try:
        db.reference(f"/users/{user_id}").update(updated_user_data)
    except (ValueError, TypeError) as ex:
        current_app.logger.error(f"Node {user_id} is invalid: {ex}")
        raise ex
    except exceptions.FirebaseError as ex:
        current_app.logger.error(f"Firebase failure while trying to update user {user_id}: {ex}")
        raise ex

    return updated_user_data
