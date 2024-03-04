from firebase_admin import db
from flask import current_app
from firebase_admin.exceptions import FirebaseError

from src.models.Medication import Medication
from src.models.Schedule import Schedule
from src.models.errors.invalid_request_error import InvalidRequestError
from src.models.errors.resource_not_found_error import ResourceNotFoundError


def get_medication(user_id: str, medication_id: str) -> Medication:
    """
    Fetches a medication from the database.

    Args:
        user_id: (str) UID for the user.
        medication_id: (str) UID for medication.

    Returns:
        Medication: The medication object.

    Raises:
        ResourceNotFoundError: If the medication is not found.
        FirebaseError: If an error occurs while interacting with the database.
    """
    try:
        medication_data = db.reference(f"/users/{user_id}/medications/{medication_id}").get()
    except FirebaseError as ex:
        current_app.logger.error(f"Firebase failure while trying to retrieve medication {medication_id}: {ex}")
        raise ex

    if medication_data is None:
        current_app.logger.error(f"Medication {medication_id} does not exist")
        raise ResourceNotFoundError(f"Medication {medication_id} does not exist")

    return Medication.from_dict(medication_data)

#
# def get_medications(query=None, page=1, limit=50):
#     """
#     Retrieves medications from the database.
#
#     Args:
#         query: (str) The query to filter the medications by. Optional.
#         page: (int) The positive, non-zero page number to retrieve. Optional.
#         limit: (int) The positive, non-zero maximum number of medications to retrieve. Optional.
#
#     Returns:
#         list[dict]: The retrieved medications.
#         total_medications: (int) The total number of medications in the database.
#
#     Raises:
#         FirebaseError: If an error occurs while interacting with the database.
#         ValueError: If the page or limit are invalid.
#     """
#     # Validate inputs
#     if page <= 0:
#         raise ValueError("Page must be a positive, non-zero integer")
#
#     if limit <= 0:
#         raise ValueError("Limit must be a positive, non-zero integer")
#
#     # Fetch medications from the database
#     db_ref = db.reference("/medications")
#     medication_data = db_ref.order_by_key().get()
#     if medication_data is None:
#         return None, None
#     medications = list(medication_data.values())
#
#     # Filter medications by query
#     if query:
#         medications = [medication for medication in medications if medication.name and query in medication.name]
#
#     # Paginate medications
#     total_medications = len(medications)
#     if page:
#         medications = medications[(page - 1) * limit:]
#     medications = medications[:limit]
#
#     return medications, total_medications


def create_medication(medication_json_dict: dict) -> Medication:
    """
    Creates a new medication in the database.

    Args:
        medication_json_dict: (dict) Dictionary containing medication data.

    Returns:
        Medication: The newly created medication.

    Raises:
        InvalidRequestError: If the request is invalid.
        ResourceNotFoundError: If the user does not exist.
        ResourceAlreadyExistsError: If the medication already exists.
        ValueError, TypeError: If an error occurs while trying to store the medication.
        FirebaseError: If an error occurs while interacting with the database.
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
    except FirebaseError as ex:
        current_app.logger.error(f"Firebase failure while trying to retrieve user {user_id}: {ex}")
        raise ex

    if user_data is None:
        current_app.logger.error(f"User {user_id} does not exist")
        raise ResourceNotFoundError(f"User {user_id} does not exist")

    try:
        # Generates UID for the medication and creates the empty node.
        medication_id = db.reference(f"/users/{user_id}/medications").push().key
    except FirebaseError as ex:
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
        db.reference(f"/users/{user_id}/medications/{medication_id}").set(new_medication.to_dict())
    except (ValueError, TypeError) as ex:
        current_app.logger.error(f"Error while trying to store medication {medication_id}: {ex}")
        raise ex
    except FirebaseError as ex:
        current_app.logger.error(f"Firebase failure while trying to store medication {medication_id}: {ex}")
        raise ex

    return new_medication


def update_medication(user_id: str, medication_id: str, medication_json_dict: dict) -> dict:
    """
    Updates an existing medication in the database. Assumes medication does exist in the database, as that should have
    been checked already when retrieving the medication.

    Args:
        user_id: (str) UID for the user.
        medication_id: (str) UID for medication.
        medication_json_dict: (dict) Dictionary containing medication data to be updated.

    Returns:
        dict: The medication data that was updated.

    Raises:
        InvalidRequestError: If the request is invalid.
        ValueError: If an error occurs while trying to store the medication.
        FirebaseError: If an error occurs while interacting with the database.

    """
    updated_medication_data = {}
    medication_keys_to_copy = [
        "container_id", "name", "nickname", "dosage"
    ]
    for key in medication_keys_to_copy:
        if key in medication_json_dict:
            updated_medication_data[key] = medication_json_dict[key]

    if "schedule" in medication_json_dict:
        updated_schedule = Schedule.from_dict(medication_json_dict["schedule"])
        if updated_schedule:
            updated_medication_data["schedule"] = updated_schedule.to_dict()

    if not updated_medication_data:
        raise InvalidRequestError("No valid fields to update")

    try:
        db.reference(f"/users/{user_id}/medications/{medication_id}").update(updated_medication_data)
    except ValueError as ex:
        current_app.logger.error(f"Error while trying to update medication {medication_id}: {ex}")
        raise ex
    except FirebaseError as ex:
        current_app.logger.error(f"Firebase failure while trying to update medication {medication_id}: {ex}")
        raise ex

    return updated_medication_data


def delete_medication(user_id: str, medication_id: str):
    """
    Deletes a medication from the database.

    Args:
        user_id: (str) The user's ID.
        medication_id: (str) The medication's ID.
        
    Returns:
        None

    Raises:
        FirebaseError: If an error occurs while interacting with the database.
    """
    try:
        db.reference(f"/users/{user_id}/medications/{medication_id}").delete()
    except ValueError as ex:
        current_app.logger.error(f"Error while trying to delete medication {medication_id}: {ex}")
        raise ex
    except FirebaseError as ex:
        current_app.logger.error(f"Firebase failure while trying to delete medication {medication_id}: {ex}")
        raise ex
    