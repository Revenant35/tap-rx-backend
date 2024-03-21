from unittest.mock import MagicMock, patch

import pytest
from firebase_admin.exceptions import FirebaseError

from src.controllers.medication_event_controller import get_medication_event, create_medication_event
from src.models.MedicationEvent import MedicationEvent
from src.models.errors.invalid_request_error import InvalidRequestError
from src.models.errors.resource_not_found_error import ResourceNotFoundError


def test_get_medication_event_when_event_is_returned_return_event(app):
    mock_db_ref = MagicMock()
    mock_user_id = "user_id"
    mock_medication_id = "medication_id"
    mock_medication_event_id = "medication_event_id"
    mock_med_event_data = {
        "medication_event_id": mock_medication_event_id,
        "user_id": mock_user_id,
        "medication_id": mock_medication_id,
        "timestamp": "2021-01-01T00:00:00Z",
        "dosage": "10mg",
    }

    with patch("firebase_admin.db.reference", return_value=mock_db_ref):
        mock_db_ref.get.return_value = mock_med_event_data
        med_event = get_medication_event(mock_user_id, mock_medication_id, mock_medication_event_id)
        assert med_event == MedicationEvent.from_dict(mock_med_event_data)


def test_get_medication_event_when_get_fails_raise_firebase_error(app):
    mock_db_ref = MagicMock()
    mock_user_id = "user_id"
    mock_medication_id = "medication_id"
    mock_medication_event_id = "medication_event_id"

    with patch("firebase_admin.db.reference", return_value=mock_db_ref):
        mock_db_ref.get.side_effect = FirebaseError(8, "test")
        with pytest.raises(FirebaseError):
            get_medication_event(mock_user_id, mock_medication_id, mock_medication_event_id)


def test_get_medication_event_when_event_doesnt_belong_to_user_raise_invalid_request_error(app):
    mock_db_ref = MagicMock()
    mock_user_id = "user_id"
    mock_medication_id = "medication_id"
    mock_medication_event_id = "medication_event_id"
    mock_med_event_data = {
        "medication_event_id": mock_medication_event_id,
        "user_id": "other_user_id",
        "medication_id": mock_medication_id,
        "timestamp": "2021-01-01T00:00:00Z",
        "dosage": "10mg",
    }

    with patch("firebase_admin.db.reference", return_value=mock_db_ref):
        mock_db_ref.get.return_value = mock_med_event_data
        with pytest.raises(InvalidRequestError):
            med_event = get_medication_event(mock_user_id, mock_medication_id, mock_medication_event_id)


def test_get_medication_event_when_event_doesnt_exist_return_none(app):
    mock_db_ref = MagicMock()
    mock_user_id = "user_id"
    mock_medication_id = "medication_id"
    mock_medication_event_id = "medication_event_id"

    with patch("firebase_admin.db.reference", return_value=mock_db_ref):
        mock_db_ref.get.return_value = None
        med_event = get_medication_event(mock_user_id, mock_medication_id, mock_medication_event_id)
        assert med_event is None


def test_create_medication_event_when_event_is_created_return_event(app):
    mock_db_ref = MagicMock()
    mock_user_id = "user_id"
    mock_medication_id = "medication_id"
    mock_medication_event_id = "medication_event_id"
    mock_timestamp = "2021-01-01T00:00:00Z"
    mock_dosage = "10mg"
    mock_medication_event_data = {
        "timestamp": mock_timestamp,
        "dosage": mock_dosage,
    }

    with patch("firebase_admin.db.reference", return_value=mock_db_ref), \
            patch("src.controllers.medication_event_controller.get_medication", return_value=MagicMock()):
        mock_db_ref.push.return_value.key = mock_medication_event_id
        med_event = create_medication_event(mock_user_id, mock_medication_id, mock_medication_event_data)
        assert med_event.medication_event_id == mock_medication_event_id
        mock_db_ref.set.assert_called_once()


def test_create_medication_event_when_data_is_missing(app):
    mock_user_id = "user_id"
    mock_medication_id = "medication_id"
    mock_dosage = "10mg"
    mock_medication_event_data = {
        "dosage": mock_dosage,
    }

    with pytest.raises(InvalidRequestError):
        create_medication_event(mock_user_id, mock_medication_id, mock_medication_event_data)


def test_create_medication_event_when_medication_doesnt_exist_raise_resource_not_found_error(app):
    mock_db_ref = MagicMock()
    mock_user_id = "user_id"
    mock_medication_id = "medication_id"
    mock_timestamp = "2021-01-01T00:00:00Z"
    mock_medication_event_data = {
        "timestamp": mock_timestamp,
    }

    with patch("firebase_admin.db.reference", return_value=mock_db_ref), \
            patch("src.controllers.medication_event_controller.get_medication", return_value=None):
        with pytest.raises(ResourceNotFoundError):
            create_medication_event(mock_user_id, mock_medication_id, mock_medication_event_data)


def test_create_medication_event_when_firebase_error_occurs_raise_firebase_error(app):
    mock_db_ref = MagicMock()
    mock_user_id = "user_id"
    mock_medication_id = "medication_id"
    mock_timestamp = "2021-01-01T00:00:00Z"
    mock_medication_event_data = {
        "timestamp": mock_timestamp,
    }

    with patch("firebase_admin.db.reference", return_value=mock_db_ref), \
            patch("src.controllers.medication_event_controller.get_medication", return_value=MagicMock()):
        mock_db_ref.push.side_effect = FirebaseError(8, "test")
        with pytest.raises(FirebaseError):
            create_medication_event(mock_user_id, mock_medication_id, mock_medication_event_data)
