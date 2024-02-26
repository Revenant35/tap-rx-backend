from firebase_admin import db, exceptions
from flask import current_app

from src.models.Medication import Medication
from src.models.Schedule import Schedule
from src.models.errors.invalid_request_error import InvalidRequestError
from src.models.errors.resource_not_found_error import ResourceNotFoundError


def create_medication(medication_json_dict: dict) -> Medication:
    """
    Creates a new medication in the database.

    Args:
        medication_json_dict: (dict) Dictionary containing medication data.

    Returns:
        Medication: The newly created medication.

    Raises:
        InvalidRequestError: If the request is invalid.
        ResourceAlreadyExistsError: If the medication already exists.
        ValueError, TypeError: If an error occurs while trying to store the medication.
        exceptions.FirebaseError: If an error occurs while interacting with the database.
    """
    try:
        name = medication_json_dict["name"]
        user_id = medication_json_dict["user_id"]
        dependent_id = medication_json_dict.get("dependent_id", None)
        container_id = medication_json_dict.get("container_id", None)
        nickname = medication_json_dict.get("nickname", None)
        dosage = medication_json_dict.get("dosage", None)
        schedule = medication_json_dict.get("schedule", None)
    except (ValueError, KeyError, TypeError) as ex:
        current_app.logger.error(f"Invalid request JSON: {ex}")
        raise InvalidRequestError

    try:
        user_data = db.reference(f"/users/{user_id}").get()
    except exceptions.FirebaseError as ex:
        current_app.logger.error(f"Firebase failure while trying to retrieve user {user_id}: {ex}")
        raise ex

    if user_data is None:
        current_app.logger.error(f"User {user_id} does not exist")
        raise ResourceNotFoundError(f"User {user_id} does not exist")

    try:
        # Generates UID for the medication and creates the empty node.
        medication_id = db.reference(f"/medications").push().key
    except exceptions.FirebaseError as ex:
        current_app.logger.error(f"Firebase failure while trying to generate medication ID: {ex}")
        raise ex

    new_medication = Medication(
        medication_id=medication_id,
        user_id=user_id,
        name=name,
        dependent_id=dependent_id,
        container_id=container_id,
        nickname=nickname,
        dosage=dosage,
        schedule=Schedule.from_dict(schedule)
    )

    try:
        db.reference(f"/medications/{medication_id}").set(new_medication.to_dict())

        user_medications = user_data.get("medications", [])
        user_medications.append(medication_id)
        db.reference(f"/users/{user_id}/medications").set(user_medications)
    except (ValueError, TypeError) as ex:
        current_app.logger.error(f"Error while trying to store medication {medication_id}: {ex}")
        raise ex
    except exceptions.FirebaseError as ex:
        current_app.logger.error(f"Firebase failure while trying to store medication {medication_id}: {ex}")
        raise ex

    return new_medication
