from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from firebase_admin.exceptions import FirebaseError

from src.controllers.medication_event_controller import (
    get_medication_event,
    create_medication_event,
    update_medication_event,
    delete_medication_event,
    get_medication_events_for_medication,
)
from src.models.MedicationEvent import MedicationEvent
from src.models.errors.invalid_request_error import InvalidRequestError
from src.models.errors.resource_not_found_error import ResourceNotFoundError


def test_get_medication_events_for_medication_when_events_are_returned_return_events(app):
    mock_db_ref = MagicMock()
    med_id = "medication_id"
    start_at = datetime.min
    end_at = datetime.utcnow()
    med_events_dict = {}
    for i in range(5):
        med_event = MedicationEvent(
            medication_event_id=f"medication_event_id_{i}",
            user_id="user_id",
            medication_id=med_id,
            timestamp=datetime.utcnow(),
        )
        med_events_dict[med_event.medication_event_id] = med_event.to_dict()

    with patch("firebase_admin.db.reference", return_value=mock_db_ref):
        mock_get = mock_db_ref.order_by_child.return_value.start_at.return_value.end_at.return_value.limit_to_last.return_value.get
        mock_get.return_value = med_events_dict
        med_events = get_medication_events_for_medication(med_id, start_at, end_at)
        assert len(med_events) == 5
        for i in range(5):
            assert med_events[i] == MedicationEvent.from_dict(med_events_dict[f"medication_event_id_{i}"])


def test_get_medication_events_for_medication_when_no_events_return_empty_list(app):
    mock_db_ref = MagicMock()
    med_id = "medication_id"
    start_at = datetime.min
    end_at = datetime.utcnow()

    with patch("firebase_admin.db.reference", return_value=mock_db_ref):
        mock_get = mock_db_ref.order_by_child.return_value.start_at.return_value.end_at.return_value.limit_to_last.return_value.get
        mock_get.return_value = None
        med_events = get_medication_events_for_medication(med_id, start_at, end_at)
        assert len(med_events) == 0


def test_get_medication_events_for_medication_when_invalid_range_is_passed_raise_invalid_request_error(app):
    med_id = "medication_id"
    start_at = datetime.max
    end_at = datetime.utcnow()

    with pytest.raises(InvalidRequestError):
         get_medication_events_for_medication(med_id, start_at, end_at)


def test_get_medication_events_for_medication_when_firebase_error_occurs_raise_firebase_error(app):
    mock_db_ref = MagicMock()
    med_id = "medication_id"
    start_at = datetime.min
    end_at = datetime.utcnow()

    with patch("firebase_admin.db.reference", return_value=mock_db_ref):
        mock_get = mock_db_ref.order_by_child.return_value.start_at.return_value.end_at.return_value.limit_to_last.return_value.get
        mock_get.side_effect = FirebaseError(8, "test")
        with pytest.raises(FirebaseError):
            get_medication_events_for_medication(med_id, start_at, end_at)


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


def test_update_medication_event_when_event_is_updated_return_updated_data(app):
    mock_db_ref = MagicMock()
    mock_user_id = "user_id"
    mock_medication_id = "medication_id"
    mock_medication_event_id = "medication_event_id"
    mock_medication_event_data = {
        "medication_id": "new_medication_id",
        "timestamp": "2021-01-01T00:00:00Z",
        "dosage": "10mg",
    }

    with patch("firebase_admin.db.reference", return_value=mock_db_ref), \
            patch("src.controllers.medication_event_controller.get_medication_event", return_value=MagicMock()):
        updated_med_event_data = update_medication_event(
            mock_user_id, mock_medication_id, mock_medication_event_id, mock_medication_event_data
        )
        assert updated_med_event_data == mock_medication_event_data
        mock_db_ref.update.assert_called_once()


def test_update_medication_event_when_no_valid_data_to_update_raise_invalid_request_error(app):
    mock_user_id = "user_id"
    mock_medication_id = "medication_id"
    mock_medication_event_id = "medication_event_id"
    mock_medication_event_data = {
        "invalid_key": "invalid_value",
    }

    with pytest.raises(InvalidRequestError):
        update_medication_event(
            mock_user_id, mock_medication_id, mock_medication_event_id, mock_medication_event_data
        )


def test_update_medication_when_event_doesnt_exist_raise_resource_not_found_error(app):
    mock_db_ref = MagicMock()
    mock_user_id = "user_id"
    mock_medication_id = "medication_id"
    mock_medication_event_id = "medication_event_id"
    mock_medication_event_data = {
        "dosage": "10mg",
    }

    with patch("firebase_admin.db.reference", return_value=mock_db_ref), \
            patch("src.controllers.medication_event_controller.get_medication_event", return_value=None):
        with pytest.raises(ResourceNotFoundError):
            update_medication_event(mock_user_id, mock_medication_id, mock_medication_event_id, mock_medication_event_data)


def test_update_medication_event_when_firebase_fails_raise_firebase_error(app):
    mock_db_ref = MagicMock()
    mock_user_id = "user_id"
    mock_medication_id = "medication_id"
    mock_medication_event_id = "medication_event_id"
    mock_medication_event_data = {
        "dosage": "10mg",
    }

    with patch("firebase_admin.db.reference", return_value=mock_db_ref), \
            patch("src.controllers.medication_event_controller.get_medication_event", return_value=MagicMock()):
        mock_db_ref.update.side_effect = FirebaseError(8, "test")
        with pytest.raises(FirebaseError):
            update_medication_event(mock_user_id, mock_medication_id, mock_medication_event_id, mock_medication_event_data)


def test_delete_medication_event_when_event_is_deleted_return(app):
    mock_db_ref = MagicMock()
    mock_user_id = "user_id"
    mock_medication_id = "medication_id"
    mock_medication_event_id = "medication_event_id"

    with patch("firebase_admin.db.reference", return_value=mock_db_ref), \
            patch("src.controllers.medication_event_controller.get_medication_event", return_value=MagicMock()):
        delete_medication_event(mock_user_id, mock_medication_id, mock_medication_event_id)
        mock_db_ref.delete.assert_called_once()


def test_delete_medication_event_when_event_doesnt_exist_raise_resource_not_found_error(app):
    mock_db_ref = MagicMock()
    mock_user_id = "user_id"
    mock_medication_id = "medication_id"
    mock_medication_event_id = "medication_event_id"

    with patch("firebase_admin.db.reference", return_value=mock_db_ref), \
            patch("src.controllers.medication_event_controller.get_medication_event", return_value=None):
        with pytest.raises(ResourceNotFoundError):
            delete_medication_event(mock_user_id, mock_medication_id, mock_medication_event_id)


def test_delete_medication_event_when_firebase_fails_raise_firebase_error(app):
    mock_db_ref = MagicMock()
    mock_user_id = "user_id"
    mock_medication_id = "medication_id"
    mock_medication_event_id = "medication_event_id"

    with patch("firebase_admin.db.reference", return_value=mock_db_ref), \
            patch("src.controllers.medication_event_controller.get_medication_event", return_value=MagicMock()):
        mock_db_ref.delete.side_effect = FirebaseError(8, "test")
        with pytest.raises(FirebaseError):
            delete_medication_event(mock_user_id, mock_medication_id, mock_medication_event_id)
