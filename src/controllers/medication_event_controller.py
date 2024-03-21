from datetime import datetime

from firebase_admin import db
from firebase_admin.exceptions import FirebaseError
from flask import current_app

from src.controllers.medication_controller import get_medication
from src.models.MedicationEvent import MedicationEvent
from src.models.errors.invalid_request_error import InvalidRequestError
from src.models.errors.resource_not_found_error import ResourceNotFoundError


def get_medication_event(user_id: str, medication_id: str, medication_event_id: str) -> MedicationEvent or None:
    """
    Fetches a medication event from the database.

    Args:
        user_id: (str) The user's ID.
        medication_id: (str) The medication's ID.
        medication_event_id: (str) The medication event's ID.

    Returns:
        MedicationEvent: The medication event object if found. Otherwise, None.

    Raises:
        InvalidRequestError: If the user does not have access to the medication event.
        FirebaseError: If an error occurs while interacting with the database.
        ValueError: If the medication event is not a dictionary.
    """
    try:
        medication_event_data = db.reference(f"/medication_event/{medication_id}/{medication_event_id}").get()
    except (ValueError, FirebaseError) as ex:
        current_app.logger.error(
            f"Failed to retrieve medication event {medication_event_id} for medication {medication_id}: {ex}"
        )
        raise FirebaseError(500, "Failed to retrieve medication event")

    if medication_event_data:
        if not isinstance(medication_event_data, dict):
            raise ValueError(
                f"Expected a dictionary from Firebase, but got a different type. Got: {medication_event_data}"
            )
        med_event = MedicationEvent.from_dict(medication_event_data)
        if med_event.user_id != user_id:
            raise InvalidRequestError("User does not have access to this medication event")
        return MedicationEvent.from_dict(medication_event_data)
    else:
        return None


def create_medication_event(user_id: str, medication_id: str, medication_event_json_dict: dict) -> MedicationEvent:
    """
    Creates a new medication event in the database.

    Args:
        user_id: (str) The user's ID.
        medication_id: (str) The medication's ID.
        medication_event_json_dict: (dict) The medication event's data.

    Returns:
        MedicationEvent: The newly created medication event.

    Raises:
        InvalidRequestError: If the request is invalid.
        ResourceNotFoundError: If the medication or user does not exist.
        FirebaseError: If an error occurs while interacting with the database.
    """
    try:
        timestamp = datetime.fromisoformat(medication_event_json_dict["timestamp"])
        dosage = medication_event_json_dict.get("dosage", None)
    except (ValueError, TypeError, KeyError):
        raise InvalidRequestError

    try:
        medication_data = get_medication(user_id, medication_id)
    except (ValueError, FirebaseError):
        current_app.logger.error(f"Failed to retrieve medication {medication_id} for user {user_id}")
        raise FirebaseError

    if medication_data is None:
        current_app.logger.error(f"Medication {medication_id} does not exist for user {user_id}")
        raise ResourceNotFoundError(f"Medication {medication_id} does not exist for user {user_id}")

    try:
        medication_event_id = db.reference(f"/medication_event/{medication_id}").push().key
    except FirebaseError as ex:
        current_app.logger.error(f"Firebase failure while trying to generate medication event ID: {ex}")
        raise ex

    new_medication_event = MedicationEvent(
        medication_event_id=medication_event_id,
        user_id=user_id,
        medication_id=medication_id,
        timestamp=timestamp,
        dosage=dosage
    )
    try:
        db.reference(f"/medication_event/{medication_id}/{medication_event_id}").set(new_medication_event.to_dict())
    except (ValueError, TypeError) as ex:
        current_app.logger.error(
            f"Failed to store medication event {medication_event_id} for medication {medication_id}: {ex}"
        )
        raise FirebaseError

    return new_medication_event


def update_medication_event(
        medication_id: str, medication_event_id: str, medication_event_json_dict: dict
) -> dict:
    """
    Updates a medication event in the database.

    Args:
        medication_id: (str) The medication's ID.
        medication_event_id: (str) The medication event's ID.
        medication_event_json_dict: (dict) The medication event's udpated data

    Returns:
        dict: The updated medication event data.

    Raises:
        InvalidRequestError: If the request is invalid.
        FirebaseError: If an error occurs while interacting with the database.
    """
    updated_medication_event_data = {}
    keys_to_copy = ["medication_id", "timestamp", "dosage"]
    for key in keys_to_copy:
        if key in medication_event_json_dict:
            updated_medication_event_data[key] = medication_event_json_dict[key]

    if not updated_medication_event_data:
        raise InvalidRequestError("No valid fields to update")

    try:
        db.reference(f"/medication_event/{medication_id}/{medication_event_id}").update(updated_medication_event_data)
    except (ValueError, FirebaseError) as ex:
        current_app.logger.error(f"Error while trying to update medication event {medication_event_id}: {ex}")
        raise FirebaseError

    return updated_medication_event_data
