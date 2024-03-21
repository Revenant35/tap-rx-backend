from firebase_admin import db
from flask import current_app
from firebase_admin.exceptions import FirebaseError

from src.models.Dependant import Dependant
from src.models.errors.resource_already_exists_error import ResourceAlreadyExistsError
from src.models.errors.invalid_request_error import InvalidRequestError
from src.models.errors.resource_not_found_error import ResourceNotFoundError


def get_dependants(user_id: str) -> tuple[list[Dependant], int]:
    """
    Fetches all dependants for a user from the database.

    Args:
        user_id: (str) UID for the user.

    Returns:
        tuple: A list of dependant objects if found and the total number of dependants for the user.

    Raises:
        FirebaseError: If an error occurs while interacting with the database.
        ValueError: If an error occurs while trying to retrieve the dependants.
        InvalidRequestError: If an error occurs from input.
    """
    if user_id is None:
        raise InvalidRequestError("User ID cannot be None")

    try:
        dependants = db.reference(f"/users/{user_id}/dependants").get()
    except ValueError as ex:
        current_app.logger.error(f"Invalid request: {ex}")
        raise InvalidRequestError
    except FirebaseError as ex:
        current_app.logger.error(
            f"Firebase failure while trying to retrieve dependants for user {user_id}: {ex}"
        )
        raise ex

    if dependants is None:
        return [], 0

    if not isinstance(dependants, list):
        raise ValueError(
            f"Expected a list from Firebase, but got a different type. Got: {dependants}"
        )

    for dependant in dependants:
        if not isinstance(dependant, dict):
            raise ValueError(
                f"Expected a dict from Firebase, but got a different type. Got: {dependants}"
            )

    dependants = [Dependant.from_dict(dependant) for dependant in dependants]
    total = len(dependants)

    return dependants, total


def get_dependant(user_id: str, dependant_id: str) -> Dependant or None:
    """
    Fetches a dependant from the database.

    Args:
        user_id: (str) UID for the user.
        dependant_id: (str) UID for the dependant.

    Returns:
        Dependant: The dependant object if found. Otherwise, None.

    Raises:
        FirebaseError: If an error occurs while interacting with the database.
        ValueError: If an error occurs while trying to retrieve the dependant.
        InvalidRequestError: If an error occurs from input.
    """
    if user_id is None:
        raise InvalidRequestError("User ID cannot be None")

    if dependant_id is None:
        raise InvalidRequestError("Dependant ID cannot be None")

    try:
        user_data = db.reference(f"/users/{user_id}").get()
    except ValueError as ex:
        current_app.logger.error(f"Invalid request: {ex}")
        raise InvalidRequestError
    except FirebaseError as ex:
        current_app.logger.error(
            f"Firebase failure while trying to retrieve user {user_id}: {ex}"
        )
        raise ex

    if user_data is None:
        current_app.logger.error(f"User {user_id} does not exist")
        raise ResourceNotFoundError(f"User {user_id} does not exist")

    try:
        dependant_data = db.reference(
            f"/users/{user_id}/dependants/{dependant_id}"
        ).get()
    except ValueError as ex:
        current_app.logger.error(f"Invalid request: {ex}")
        raise InvalidRequestError
    except FirebaseError as ex:
        current_app.logger.error(
            f"Firebase failure while trying to retrieve dependant {dependant_id}: {ex}"
        )
        raise ex

    if dependant_data is not None:
        return Dependant.from_dict(dependant_data)
    else:
        return None


def create_dependant(user_id: str, dependant_json_dict: dict) -> Dependant or None:
    """
    Creates a new dependant in the database.

    Args:
        user_id: (str) UID for the user.
        dependant_json_dict: (dict) A dictionary containing the dependant's data.

    Returns:
        Dependant: The newly created dependant object.

    Raises:
        FirebaseError: If an error occurs while interacting with the database.
        InvalidRequestError: If the request is invalid.
        ResourceNotFoundError: If the user does not exist.
    """
    if user_id is None:
        raise InvalidRequestError("User ID cannot be None")

    try:
        first_name = dependant_json_dict["first_name"]
        last_name = dependant_json_dict["last_name"]
        phone = dependant_json_dict.get("phone", None)
    except (ValueError, KeyError, TypeError) as ex:
        current_app.logger.error(f"Invalid request JSON: {ex}")
        raise InvalidRequestError

    if not first_name or not last_name:
        current_app.logger.error("First name and last name are required")
        raise InvalidRequestError("First name and last name are required")

    try:
        user_data = db.reference(f"/users/{user_id}").get()
    except ValueError as ex:
        current_app.logger.error(f"Invalid request: {ex}")
        raise InvalidRequestError
    except FirebaseError as ex:
        current_app.logger.error(
            f"Firebase failure while trying to retrieve user {user_id}: {ex}"
        )
        raise ex

    if user_data is None:
        current_app.logger.error(f"User {user_id} does not exist")
        raise ResourceNotFoundError(f"User {user_id} does not exist")

    try:
        dependant_id = db.reference(f"/users/{user_id}/dependants").push().key
    except (ValueError, TypeError) as ex:
        current_app.logger.error(f"Invalid request: {ex}")
        raise InvalidRequestError
    except FirebaseError as ex:
        current_app.logger.error(
            f"Firebase failure while trying to generate dependant ID: {ex}"
        )
        raise ex

    new_dependant = Dependant(
        dependant_id=dependant_id,
        first_name=first_name,
        last_name=last_name,
        phone=phone,
    )

    try:
        db.reference(f"/users/{user_id}/dependants/{dependant_id}").set(
            new_dependant.to_dict()
        )
    except (ValueError, TypeError) as ex:
        current_app.logger.error(f"Invalid request: {ex}")
        raise InvalidRequestError
    except FirebaseError as ex:
        current_app.logger.error(
            f"Firebase failure while trying to store dependant {dependant_id}: {ex}"
        )
        raise ex

    return new_dependant


def update_dependant(
    user_id: str, dependant_id: str, dependant_json_dict: dict
) -> Dependant:
    """
    Updates a dependant in the database.

    Args:
        user_id: (str) UID for the user.
        dependant_id: (str) UID for the dependant.
        dependant_json_dict: (dict) A dictionary containing the dependant's data.

    Returns:
        Dependant: The updated dependant object.

    Raises:
        FirebaseError: If an error occurs while interacting with the database.
        InvalidRequestError: If the request is invalid.
        ResourceNotFoundError: If the user or dependant does not exist.
    """
    if user_id is None:
        raise InvalidRequestError("User ID cannot be None")

    if dependant_id is None:
        raise InvalidRequestError("Dependant ID cannot be None")

    try:
        user_data = db.reference(f"/users/{user_id}").get()
    except ValueError as ex:
        current_app.logger.error(f"Invalid request: {ex}")
        raise InvalidRequestError
    except FirebaseError as ex:
        current_app.logger.error(
            f"Firebase failure while trying to retrieve user {user_id}: {ex}"
        )
        raise ex

    if user_data is None:
        current_app.logger.error(f"User {user_id} does not exist")
        raise ResourceNotFoundError(f"User {user_id} does not exist")

    try:
        dependant_data = db.reference(
            f"/users/{user_id}/dependants/{dependant_id}"
        ).get()
    except ValueError as ex:
        current_app.logger.error(f"Invalid request: {ex}")
        raise InvalidRequestError
    except FirebaseError as ex:
        current_app.logger.error(
            f"Firebase failure while trying to retrieve dependant {dependant_id}: {ex}"
        )
        raise ex

    if dependant_data is None:
        current_app.logger.error(f"Dependant {dependant_id} does not exist")
        raise ResourceNotFoundError(f"Dependant {dependant_id} does not exist")

    try:
        first_name = dependant_json_dict.get("first_name", dependant_data["first_name"])
        last_name = dependant_json_dict.get("last_name", dependant_data["last_name"])
        phone = dependant_json_dict.get("phone", dependant_data.get("phone", None))
    except (ValueError, KeyError, TypeError) as ex:
        current_app.logger.error(f"Invalid request JSON: {ex}")
        raise InvalidRequestError

    if not first_name or not last_name:
        current_app.logger.error("First name and last name are required")
        raise InvalidRequestError("First name and last name are required")

    updated_dependant = Dependant(
        dependant_id=dependant_id,
        first_name=first_name,
        last_name=last_name,
        phone=phone,
    )

    try:
        db.reference(f"/users/{user_id}/dependants/{dependant_id}").set(
            updated_dependant.to_dict()
        )
    except (ValueError, TypeError) as ex:
        current_app.logger.error(f"Invalid request: {ex}")
        raise InvalidRequestError
    except FirebaseError as ex:
        current_app.logger.error(
            f"Firebase failure while trying to update dependant {dependant_id}: {ex}"
        )
        raise ex

    return updated_dependant


def delete_dependant(user_id: str, dependant_id: str) -> None:
    """
    Deletes a dependant from the database.

    Args:
        user_id: (str) UID for the user.
        dependant_id: (str) UID for the dependant.

    Returns:
        None

    Raises:
        FirebaseError: If an error occurs while interacting with the database.
        ValueError: If an error occurs while trying to delete the dependant.
    """
    if user_id is None:
        raise InvalidRequestError("User ID cannot be None")

    if dependant_id is None:
        raise InvalidRequestError("Dependant ID cannot be None")

    try:
        user_data = db.reference(f"/users/{user_id}").get()
    except ValueError as ex:
        current_app.logger.error(f"Invalid request: {ex}")
        raise InvalidRequestError
    except FirebaseError as ex:
        current_app.logger.error(
            f"Firebase failure while trying to retrieve user {user_id}: {ex}"
        )
        raise ex

    if user_data is None:
        current_app.logger.error(f"User {user_id} does not exist")
        raise ResourceNotFoundError(f"User {user_id} does not exist")

    try:
        dependant_data = db.reference(
            f"/users/{user_id}/dependants/{dependant_id}"
        ).get()
    except ValueError as ex:
        current_app.logger.error(f"Invalid request: {ex}")
        raise InvalidRequestError
    except FirebaseError as ex:
        current_app.logger.error(
            f"Firebase failure while trying to retrieve dependant {dependant_id}: {ex}"
        )
        raise ex

    if dependant_data is None:
        current_app.logger.error(f"Dependant {dependant_id} does not exist")
        raise ResourceNotFoundError(f"Dependant {dependant_id} does not exist")

    try:
        db.reference(f"/users/{user_id}/dependants/{dependant_id}").delete()
    except ValueError as ex:
        current_app.logger.error(f"Invalid request: {ex}")
        raise InvalidRequestError
    except FirebaseError as ex:
        current_app.logger.error(
            f"Firebase failure while trying to delete dependant {dependant_id}: {ex}"
        )
        raise ex
