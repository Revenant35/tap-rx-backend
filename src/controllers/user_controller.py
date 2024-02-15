from firebase_admin import db, exceptions
from flask import current_app

from src.models.User import User
from src.models.errors.invalid_request_error import InvalidRequestError
from src.models.errors.user_already_exists_error import UserAlreadyExistsError
from src.models.errors.user_not_found_error import UserNotFoundError


def get_users(start_at=None, limit=50):
    """
    Fetches a list of users from the database.
    Args:
        start_at: (str) UID to start at, for cursor-based pagination
        limit: (int) Maximum number of users to fetch

    Returns:
        list: List of user data, and the next page cursor (UID or None)

    Raises:
        ValueError, TypeError, exceptions.FirebaseError: If an error occurs while trying to fetch the users.
    """
    db_ref = db.reference("/users")

    # Start at a specific user UID (if provided) and limit the number of results
    query = db_ref.order_by_key()
    if start_at:
        query = query.start_at(start_at)
    users_data = query.limit_to_first(limit + 1).get()  # Fetch one extra to check for next page

    # Determine if there's a next page
    users = list(users_data.items())
    next_page = None
    if len(users) > limit:
        next_page = users[-1][0]  # Use the second last item's UID as the next page cursor
        users = users[:-1]  # Remove the extra item

    users = [user[1] for user in users]

    return users, next_page


def get_user(user_id):
    """
    Fetches a user from the database.
    Args:
        user_id: (str) Username for user.

    Returns:
        The user's data.

    Raises:
        UserNotFoundError: If the user is not found.
        ValueError, TypeError, exceptions.FirebaseError: If an error occurs while trying to fetch the user.
    """

    user_data = db.reference(f"/users/{user_id}").get()
    if user_data is None:
        raise UserNotFoundError
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
        UserAlreadyExistsError: If the user already exists.
        ValueError, TypeError, exceptions.FirebaseError: If an error occurs while trying to store the user.
    """

    user_data = db.reference(f"/users/{user_id}").get()
    if user_data is not None:
        current_app.logger.error(f"User {user_id} already exists")
        raise UserAlreadyExistsError

    try:
        first_name = user_json_dict["first_name"]
        last_name = user_json_dict["last_name"]
        phone = user_json_dict.get("phone", None)
        dependents = user_json_dict.get("dependents", [])
        guardians = user_json_dict.get("guardians", [])
    except (ValueError, KeyError) as ex:
        current_app.logger.error(f"Invalid request JSON: {ex}")
        raise InvalidRequestError

    new_user = User(
        user_id=user_id,
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        dependents=dependents,
        guardians=guardians
    )

    try:
        db.reference(f"/users/{user_id}").set(new_user.to_dict())
    except (ValueError, TypeError, exceptions.FirebaseError) as ex:
        current_app.logger.error(f"Node {user_id} is invalid: {ex}")
        raise ex

    return new_user


def update_user(user_id: str, user_json_dict: dict) -> User:
    """
    Updates an existing user in the database.

    Args:
        user_id: (str) Username for user.
        user_json_dict: (dict) Dictionary containing user data to be updated.

    Returns:
        User: The updated user.

    Raises:
        UserNotFoundError: If the user is not found.
        ValueError, TypeError, exceptions.FirebaseError: If an error occurs while trying to update the user.
    """
    user_data = db.reference(f"/users/{user_id}").get()
    if user_data is None:
        current_app.logger.error(f"User {user_id} not exists")
        raise UserNotFoundError

    user = User.from_dict(user_data)

    try:
        first_name = user_json_dict.get("first_name", None)
        last_name = user_json_dict.get("last_name", None)
        phone = user_json_dict.get("phone", None)
        dependents = user_json_dict.get("dependents", [])
        guardians = user_json_dict.get("guardians", [])
    except (ValueError, KeyError) as ex:
        current_app.logger.error(f"Invalid request JSON: {ex}")
        raise InvalidRequestError

    if first_name:
        user.first_name = first_name
    if last_name:
        user.last_name = last_name
    if phone:
        user.phone = phone
    if dependents:
        user.dependents = dependents
    if guardians:
        user.guardians = guardians

    try:
        db.reference(f"/users/{user_id}").set(user.to_dict())
    except (ValueError, TypeError, exceptions.FirebaseError) as ex:
        current_app.logger.error(f"Node {user_id} is invalid: {ex}")
        raise ex

    return user
