from datetime import datetime, timedelta

from firebase_admin import db
from firebase_admin.exceptions import FirebaseError
from flask import current_app

from src.controllers.medication_controller import get_medication
from src.controllers.user_controller import get_user
from src.models.MedicationEvent import MedicationEvent
from src.models.User import User
from src.models.errors.invalid_request_error import InvalidRequestError
from src.models.errors.resource_not_found_error import ResourceNotFoundError
from src.utils.constants import GET_MED_EVENTS_FOR_USER_NEXT_TOKEN_DELIMITER, MAX_MEDICATION_EVENTS_PER_PAGE
from src.utils.pagination import parse_start_tkn, create_next_token


def get_medication_event(user_id: str, medication_id: str, medication_event_id: str) -> MedicationEvent | None:
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
        medication_event_data = db.reference(f"/medication_events/{medication_id}/{medication_event_id}").get()
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


def get_medication_events_for_user(
        user_id: str,
        start_at: datetime = datetime.min,
        end_at: datetime = datetime.utcnow(),
        limit: int = MAX_MEDICATION_EVENTS_PER_PAGE,
        start_token: str = None,
) -> tuple[list[MedicationEvent], str | None]:
    """
    Retrieves medication events for a user from the database from a specified range. The events are ordered by
    medication id and then timestamp in ascending order. The number of events returned will be limited by the limit
    parameter. Pagination is supported using the start_token parameter. Will return the events and the next token for
    the next page if there is one.

    Args:
        user_id: (str) The user's ID.
        start_at: (datetime) The start date for the range of events to retrieve. Optional.
        end_at: (datetime) The end date for the range of events to retrieve. Optional.
        limit: (int) The maximum number of events to retrieve. Optional.
        start_token: (str) The token to retrieve the next page of events. Optional.

    Returns:
        tuple[list[MedicationEvent], str | None]: A list of medication events and the next token for pagination.

    Raises:
        InvalidRequestError: If the request is invalid.
        FirebaseError: If an error occurs while interacting with the database.
        ValueError: If the input to create the next_token is invalid.
    """
    # TODO: Use `get_medications` to get a user's medications.
    #  Using `get_user` for now until `get_medications` is stable.
    try:
        user = User.from_dict(get_user(user_id))
    except (ValueError, TypeError) as ex:
        current_app.logger.error(f"Failed to retrieve user {user_id}: {ex}")
        raise FirebaseError(500, f"Failed to retrieve user {user_id}")

    # sort medication_ids to ensure consistent pagination
    medication_ids = list(user.medications.keys())
    medication_ids.sort()
    medication_events = []
    start_token_medication_id, start_token_end_at = parse_start_tkn(start_token, GET_MED_EVENTS_FOR_USER_NEXT_TOKEN_DELIMITER, 2)

    for medication_id in medication_ids:
        if start_token_medication_id is None or medication_id >= start_token_medication_id:
            if medication_id == start_token_medication_id:
                query_end_at = start_token_end_at
            else:
                query_end_at = end_at

            try:
                medication_events.extend(
                    get_medication_events_for_medication(
                        medication_id, start_at, query_end_at, limit - len(medication_events)
                    )
                )
            except ValueError as ex:
                current_app.logger.error(f"Failed to retrieve medication events for medication {medication_id}: {ex}")
                raise FirebaseError(500, "Failed to retrieve medication events")

            if len(medication_events) == limit:
                try:
                    next_token = create_next_token(
                        [medication_id, medication_events[-1].timestamp + timedelta(microseconds=-1)],
                        GET_MED_EVENTS_FOR_USER_NEXT_TOKEN_DELIMITER
                    )
                except ValueError as ex:
                    current_app.logger.error(f"Failed to create next token for medication events: {ex}")
                    raise ex
                return medication_events, next_token
    return medication_events, None


def get_medication_events_for_medication_controller(
        user_id: str,
        medication_id: str,
        start_at: datetime = datetime.min,
        end_at: datetime = datetime.utcnow(),
        limit: int = MAX_MEDICATION_EVENTS_PER_PAGE,
        start_token: str = None
) -> tuple[list[MedicationEvent], str | None]:
    """
    Uses the get_medication_events_for_medication function to retrieve medication events for a medication. Handles the
    authorization and pagination of the data retrieval.

    Args:
        user_id: (str) The user's ID.
        medication_id: (str) The medication's ID.
        start_at: (datetime) The start date for the range of events to retrieve. Optional.
        end_at: (datetime) The end date for the range of events to retrieve. Optional.
        limit: (int) The maximum number of events to retrieve. Optional.
        start_token: (str) The token to retrieve the next page of events. Optional.

    Returns:
        tuple[list[MedicationEvent], str]: A list of medication events and the next token for pagination.

    Raises:
        InvalidRequestError: If the request is invalid.
        FirebaseError: If an error occurs while interacting with the database.
    """
    # TODO: Use `get_medications` to get a user's medications.
    #  Using `get_user` for now until `get_medications` is stable.
    try:
        user = User.from_dict(get_user(user_id))
    except (ValueError, TypeError) as ex:
        current_app.logger.error(f"Failed to retrieve user {user_id}: {ex}")
        raise FirebaseError(500, f"Failed to retrieve user {user_id}")
    # TODO: add authorization for monitoring users to access their monitored users events
    if medication_id not in user.medications.keys():
        raise InvalidRequestError("User is not authorized to access events for this medication")

    if start_at > end_at:
        current_app.logger.error(f"Invalid date range: {start_at} > {end_at}")
        raise InvalidRequestError("Invalid date range")

    if start_token not in [None, ""]:
        try:
            end_at = datetime.fromisoformat(start_token)
        except (ValueError, TypeError):
            raise InvalidRequestError("Invalid date format for start_token. Please use ISO 8601 format.")

    try:
        medication_events = get_medication_events_for_medication(medication_id, start_at, end_at, limit)
    except ValueError as ex:
        current_app.logger.error(f"Failed to retrieve medication events for medication {medication_id}: {ex}")
        raise FirebaseError(500, "Failed to retrieve medication events")

    if len(medication_events) < limit:
        next_token = None
    else:
        next_token = (medication_events[-1].timestamp + timedelta(microseconds=-1)).isoformat()

    return medication_events, next_token


def get_medication_events_for_medication(
        medication_id: str,
        start_at: datetime = datetime.min,
        end_at: datetime = datetime.utcnow(),
        limit: int = MAX_MEDICATION_EVENTS_PER_PAGE
) -> list[MedicationEvent]:
    """
    Retrieves medication events for a medication from the database from a specified range. The events are ordered by the
    timestamp in ascending order. The number of events returned will be limited by the limit parameter which is capped
    at 250.

    Args:
        medication_id: (str) The medication's ID.
        start_at: (datetime) The start date for the range of events to retrieve. Optional.
        end_at: (datetime) The end date for the range of events to retrieve. Optional.
        limit: (int) The maximum number of events to retrieve. Optional.

    Returns:
        list[MedicationEvent]: A list of medication events.

    Raises:
        InvalidRequestError: If the request is invalid.
        FirebaseError: If an error occurs while interacting with the database.
        ValueError: If the medication events are not a dictionary.
    """
    if start_at > end_at:
        current_app.logger.error(f"Invalid date range: {start_at} > {end_at}")
        raise InvalidRequestError("Invalid date range")

    if not 0 < limit <= MAX_MEDICATION_EVENTS_PER_PAGE:
        current_app.logger.error(f"Invalid limit value: {limit}")
        raise InvalidRequestError(
            f"Invalid limit value. "
            f"Please use a positive integer value that is less than or equal to {MAX_MEDICATION_EVENTS_PER_PAGE}."
        )

    try:
        medication_events = db.reference(f"/medication_events/{medication_id}")\
            .order_by_child("timestamp")\
            .start_at(start_at.isoformat())\
            .end_at(end_at.isoformat())\
            .limit_to_last(limit)\
            .get()
    except (FirebaseError, ValueError) as ex:
        current_app.logger.error(f"Failed to retrieve medication events for medication {medication_id}: {ex}")
        raise FirebaseError(500, "Failed to retrieve medication events")

    if not medication_events:
        return []

    if not isinstance(medication_events, dict):
        raise ValueError(f"Expected a dictionary from Firebase, but got a different type. Got: {medication_events}")

    return [MedicationEvent.from_dict(medication_event_data) for medication_event_data in medication_events.values()]


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
        medication_event_id = db.reference(f"/medication_events/{medication_id}").push().key
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
        db.reference(f"/medication_events/{medication_id}/{medication_event_id}").set(new_medication_event.to_dict())
    except (ValueError, TypeError) as ex:
        current_app.logger.error(
            f"Failed to store medication event {medication_event_id} for medication {medication_id}: {ex}"
        )
        raise FirebaseError

    return new_medication_event


def update_medication_event(
        user_id: str, medication_id: str, medication_event_id: str, medication_event_json_dict: dict
) -> dict:
    """
    Updates a medication event in the database.

    Args:
        user_id: (str) The user's ID.
        medication_id: (str) The medication's ID.
        medication_event_id: (str) The medication event's ID.
        medication_event_json_dict: (dict) The medication event's udpated data

    Returns:
        dict: The updated medication event data.

    Raises:
        InvalidRequestError: If the request is invalid.
        ResourceNotFoundError: If the medication event does not exist.
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
        medication_event = get_medication_event(user_id, medication_id, medication_event_id)
    except ValueError:
        current_app.logger.error(f"Failed to retrieve medication event {medication_event_id}")
        raise FirebaseError(500, "Failed to retrieve medication event")

    if medication_event is None:
        raise ResourceNotFoundError(f"Medication event {medication_event_id} not found")

    try:
        db.reference(f"/medication_events/{medication_id}/{medication_event_id}").update(updated_medication_event_data)
    except (ValueError, FirebaseError) as ex:
        current_app.logger.error(f"Error while trying to update medication event {medication_event_id}: {ex}")
        raise FirebaseError(500, "Failed to update medication event")

    return updated_medication_event_data


def delete_medication_event(user_id: str, medication_id: str, medication_event_id: str) -> None:
    """
    Deletes a medication event from the database.

    Args:
        user_id: (str) The user's ID.
        medication_id: (str) The medication's ID.
        medication_event_id: (str) The medication event's ID.

    Raises:
        InvalidRequestError: If the user does not have access to the medication event.
        ResourceNotFoundError: If the medication event does not exist.
        FirebaseError: If an error occurs while interacting with the database.
    """
    try:
        medication_event = get_medication_event(user_id, medication_id, medication_event_id)
    except ValueError:
        current_app.logger.error(f"Failed to retrieve medication event {medication_event_id}")
        raise FirebaseError(500, "Failed to retrieve medication event")

    if medication_event is None:
        raise ResourceNotFoundError(f"Medication event {medication_event_id} not found")

    try:
        db.reference(f"/medication_events/{medication_id}/{medication_event_id}").delete()
    except FirebaseError as ex:
        current_app.logger.error(f"Failed to delete medication event {medication_event_id}: {ex}")
        raise FirebaseError(500, "Failed to delete medication event")
