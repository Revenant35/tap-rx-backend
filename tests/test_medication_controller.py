from unittest.mock import MagicMock, patch

import pytest
from firebase_admin.exceptions import FirebaseError

from src.controllers.medication_controller import create_medication, get_medication, update_medication, \
    delete_medication
from src.models.Medication import Medication
from src.models.Schedule import Schedule
from src.models.errors.invalid_request_error import InvalidRequestError
from src.models.errors.resource_not_found_error import ResourceNotFoundError


def test_get_medication_when_medication_is_fetched_return_medication(app):
    mock_db_ref = MagicMock()
    mock_medication_id = "test_medication"
    mock_medication_data = {
        "medication_id": mock_medication_id,
        "user_id": "test_user",
        "name": "Test Medication",
    }

    with patch("firebase_admin.db.reference", return_value=mock_db_ref):
        mock_db_ref.get.return_value = mock_medication_data
        medication = get_medication(mock_medication_data)
        assert medication == Medication.from_dict(mock_medication_data)


def test_get_medication_when_get_fails_raise_firebase_error(app):
    mock_db_ref = MagicMock()
    mock_medication_id = "test_medication"

    with patch("firebase_admin.db.reference", return_value=mock_db_ref):
        mock_db_ref.get.side_effect = FirebaseError(8, "test")
        with pytest.raises(FirebaseError):
            get_medication(mock_medication_id)


def test_get_medication_when_medication_is_not_found_raise_resource_not_found_error(app):
    mock_db_ref = MagicMock()
    mock_medication_id = "test_medication"

    with patch("firebase_admin.db.reference", return_value=mock_db_ref):
        mock_db_ref.get.return_value = None
        with pytest.raises(ResourceNotFoundError):
            get_medication(mock_medication_id)


def test_create_medication_when_medication_is_created_return_medication(app):
    mock_db_ref = MagicMock()
    mock_user_id = "test_user"
    mock_medication_id = "test_medication"
    mock_name = "Test Medication"
    mock_container_id = "test_container"
    mock_nickname = "Test Nickname"
    mock_dosage = "Test Dosage"
    mock_schedule = {
        "minute": "0",
        "hour": "8"
    }
    mock_json_dict = {
        "user_id": mock_user_id,
        "name": mock_name,
        "container_id": mock_container_id,
        "nickname": mock_nickname,
        "dosage": mock_dosage,
        "schedule": mock_schedule
    }

    medication = Medication(
        medication_id=mock_medication_id,
        user_id=mock_user_id,
        name=mock_name,
        container_id=mock_container_id,
        nickname=mock_nickname,
        dosage=mock_dosage,
        schedule=Schedule.from_dict(mock_schedule)
    )

    with patch("firebase_admin.db.reference", return_value=mock_db_ref):
        mock_db_ref.get.return_value = MagicMock()
        mock_db_ref.push.return_value = MagicMock(key=mock_medication_id)
        mock_db_ref.child.return_value.set.return_value = None

        created_medication = create_medication(mock_json_dict)

        assert mock_db_ref.push.called_once()
        assert mock_db_ref.child.called_once_with(mock_medication_id)

        mock_user_medications = [mock_medication_id]
        assert mock_db_ref.child.return_value.set.called_once_with(mock_user_medications)
        assert mock_db_ref.child.return_value.set.called_once_with(medication.to_dict())
        assert medication == created_medication


def test_create_medication_when_invalid_request_raise_invalid_request_error(app):
    mock_name = "Test Medication"
    mock_json_dict = {
        "name": mock_name,
    }

    with pytest.raises(InvalidRequestError):
        create_medication(mock_json_dict)


def test_create_medication_when_get_fails_raise_firebase_error(app):
    mock_db_ref = MagicMock()
    mock_user_id = "test_user"
    mock_name = "Test Medication"

    mock_json_dict = {
        "user_id": mock_user_id,
        "name": mock_name,

    }

    with patch("firebase_admin.db.reference", return_value=mock_db_ref):
        mock_db_ref.get.side_effect = FirebaseError(8, "test")
        with pytest.raises(FirebaseError):
            create_medication(mock_json_dict)


def test_create_medication_when_user_doesnt_exist_raise_resource_not_found_error(app):
    mock_db_ref = MagicMock()
    mock_user_id = "test_user"
    mock_name = "Test Medication"

    mock_json_dict = {
        "user_id": mock_user_id,
        "name": mock_name,

    }

    with patch("firebase_admin.db.reference", return_value=mock_db_ref):
        mock_db_ref.get.return_value = None
        with pytest.raises(ResourceNotFoundError):
            create_medication(mock_json_dict)


def test_create_medication_when_push_fails_raise_firebase_error(app):
    mock_db_ref = MagicMock()
    mock_user_id = "test_user"
    mock_medication_id = "test_medication"
    mock_name = "Test Medication"

    mock_json_dict = {
        "user_id": mock_user_id,
        "name": mock_name,

    }

    with patch("firebase_admin.db.reference", return_value=mock_db_ref):
        mock_db_ref.get.return_value = MagicMock()
        mock_db_ref.push.side_effect = FirebaseError(8, "test")
        with pytest.raises(FirebaseError):
            create_medication(mock_json_dict)


def test_create_medication_when_medication_to_be_stored_is_invalid_raise_value_error(app):
    mock_db_ref = MagicMock()
    mock_user_id = "test_user"
    mock_medication_id = "test_medication"
    mock_name = "Test Medication"

    mock_json_dict = {
        "user_id": mock_user_id,
        "name": mock_name,

    }

    with patch("firebase_admin.db.reference", return_value=mock_db_ref):
        mock_db_ref.get.return_value = MagicMock()
        mock_db_ref.push.return_value = MagicMock(key=mock_medication_id)
        mock_db_ref.set.side_effect = ValueError()
        with pytest.raises(ValueError):
            create_medication(mock_json_dict)


def test_create_medication_when_set_fails_raise_firebase_error(app):
    mock_db_ref = MagicMock()
    mock_user_id = "test_user"
    mock_medication_id = "test_medication"
    mock_name = "Test Medication"

    mock_json_dict = {
        "user_id": mock_user_id,
        "name": mock_name,

    }

    with patch("firebase_admin.db.reference", return_value=mock_db_ref):
        mock_db_ref.get.return_value = MagicMock()
        mock_db_ref.push.return_value = MagicMock(key=mock_medication_id)
        mock_db_ref.set.side_effect = FirebaseError(8, "test")
        with pytest.raises(FirebaseError):
            create_medication(mock_json_dict)


def test_update_medication_when_medication_is_updated_return_medication(app):
    mock_db_ref = MagicMock()
    mock_medication_id = "test_medication"
    mock_medication_json_dict = {
        "dosage": "Test Dosage",
        "schedule": {
            "minute": "0",
            "hour": "8"
        },
        "invalid_key": "invalid value"
    }
    mock_updated_data = {
        "dosage": "Test Dosage",
        "schedule": {
            "minute": "0",
            "hour": "8"
        },
    }

    with patch("firebase_admin.db.reference", return_value=mock_db_ref):
        mock_db_ref.child.return_value.update.return_value = None

        updated_medication_data = update_medication(mock_medication_id, mock_medication_json_dict)

        assert mock_db_ref.child.called_once_with(mock_medication_id)
        assert mock_db_ref.child.return_value.set.called_once_with(mock_updated_data)
        assert updated_medication_data == mock_updated_data


def test_update_medication_when_no_valid_data_to_be_updated_raise_invalid_request_error(app):
    mock_medication_id = "test_medication"
    mock_medication_json_dict = {
        "invalid_key": "invalid value"
    }

    with pytest.raises(InvalidRequestError):
        update_medication(mock_medication_id, mock_medication_json_dict)


def test_update_medication_when_no_valid_schedule_data_dont_update_schedule(app):
    mock_db_ref = MagicMock()
    mock_medication_id = "test_medication"
    mock_medication_json_dict = {
        "dosage": "Test Dosage",
        "schedule": {
            "invalid_key": "invalid value"
        }
    }
    mock_updated_data = {
        "dosage": "Test Dosage",
    }

    with patch("firebase_admin.db.reference", return_value=mock_db_ref):
        mock_db_ref.child.return_value.update.return_value = None

        updated_medication_data = update_medication(mock_medication_id, mock_medication_json_dict)

        assert mock_db_ref.child.called_once_with(mock_medication_id)
        assert mock_db_ref.child.return_value.set.called_once_with(mock_updated_data)
        assert updated_medication_data == mock_updated_data


def test_update_medication_when_update_fails_raise_firebase_error(app):
    mock_db_ref = MagicMock()
    mock_medication_id = "test_medication"
    mock_medication_json_dict = {
        "dosage": "Test Dosage",
    }

    with patch("firebase_admin.db.reference", return_value=mock_db_ref):
        mock_db_ref.update.side_effect = FirebaseError(8, "test")
        with pytest.raises(FirebaseError):
            update_medication(mock_medication_id, mock_medication_json_dict)


def test_delete_medication_when_medication_is_deleted_return_none(app):
    mock_db_ref = MagicMock()
    mock_medication_id = "test_medication"

    with patch("firebase_admin.db.reference", return_value=mock_db_ref):
        mock_db_ref.delete.return_value = None
        delete_medication(mock_medication_id)
        assert mock_db_ref.delete.called_once_with(mock_medication_id)


def test_delete_medication_when_delete_fails_raise_firebase_error(app):
    mock_db_ref = MagicMock()
    mock_medication_id = "test_medication"

    with patch("firebase_admin.db.reference", return_value=mock_db_ref):
        mock_db_ref.delete.side_effect = FirebaseError(8, "test")
        with pytest.raises(FirebaseError):
            delete_medication(mock_medication_id)


def test_delete_medication_when_medication_doesnt_exist_raise_resource_not_found_error(app):
    mock_db_ref = MagicMock()
    mock_medication_id = "test_medication"

    with patch("firebase_admin.db.reference", return_value=mock_db_ref):
        mock_db_ref.delete.return_value = None
        mock_db_ref.delete.side_effect = ValueError()
        with pytest.raises(ValueError):
            delete_medication(mock_medication_id)
