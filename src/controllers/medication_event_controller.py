from datetime import datetime

from firebase_admin import db
from firebase_admin.exceptions import FirebaseError
from flask import current_app

from src.controllers.medication_controller import get_medication
from src.models.MedicationEvent import MedicationEvent
from src.models.errors.invalid_request_error import InvalidRequestError
from src.models.errors.resource_not_found_error import ResourceNotFoundError


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
        medication_id=medication_id,
        timestamp=timestamp,
        dosage=dosage
    )
    try:
        db.reference(f"/medication_event/{medication_id}/{medication_event_id}").set(new_medication_event.to_dict())
    except (ValueError, TypeError) as ex:
        current_app.logger.error(f"Failed to store medication event {medication_event_id} for medication {medication_id}: {ex}")
        raise FirebaseError

    return new_medication_event

