from unittest.mock import MagicMock, patch

import pytest
from firebase_admin.exceptions import FirebaseError

from src.controllers.user_controller import create_user, update_user
from src.models.User import User
from src.models.errors.invalid_request_error import InvalidRequestError
from src.models.errors.resource_already_exists_error import ResourceAlreadyExistsError
from src.models.errors.resource_not_found_error import ResourceNotFoundError


def test_create_user_when_user_is_created_return_user(app):
    mock_db_users_ref = MagicMock()
    mock_user_id = "test_user"
    mock_first_name = "Test"
    mock_last_name = "User"
    mock_phone = "1234567890"
    mock_json_dict = {
        "user_id": mock_user_id,
        "first_name": mock_first_name,
        "last_name": mock_last_name,
        "phone": mock_phone
    }

    user = User(user_id=mock_user_id, first_name=mock_first_name, last_name=mock_last_name, phone=mock_phone)

    with patch("firebase_admin.db.reference", return_value=mock_db_users_ref):
        mock_db_users_ref.get.return_value = None
        mock_db_users_ref.set.return_value = None

        created_user = create_user(mock_user_id, mock_json_dict)

        assert mock_db_users_ref.set.called_once_with(user.to_dict())
        assert user == created_user


def test_create_user_when_json_is_invalid_raise_invalid_request_error(app):
    mock_db_users_ref = MagicMock()
    mock_user_id = "test_user"
    mock_first_name = "Test"
    mock_json_dict = {
        "user_id": mock_user_id,
        "first_name": mock_first_name,
    }

    with patch("firebase_admin.db.reference", return_value=mock_db_users_ref):
        mock_db_users_ref.get.return_value = None

        with pytest.raises(InvalidRequestError):
            create_user(mock_user_id, mock_json_dict)


def test_create_user_when_get_user_fails_raise_firebase_error(app):
    mock_db_users_ref = MagicMock()
    mock_user_id = "test_user"
    mock_first_name = "Test"
    mock_last_name = "User"
    mock_json_dict = {
        "user_id": mock_user_id,
        "first_name": mock_first_name,
        "last_name": mock_last_name,
    }

    with patch("firebase_admin.db.reference", return_value=mock_db_users_ref):
        mock_db_users_ref.get.side_effect = FirebaseError(8, "test")
        with pytest.raises(FirebaseError):
            create_user(mock_user_id, mock_json_dict)


def test_create_user_when_user_exists_raise_user_already_exists_error(app):
    mock_db_users_ref = MagicMock()
    mock_user_id = "test_user"
    mock_first_name = "Test"
    mock_last_name = "User"
    mock_json_dict = {
        "user_id": mock_user_id,
        "first_name": mock_first_name,
        "last_name": mock_last_name,
    }

    with patch("firebase_admin.db.reference", return_value=mock_db_users_ref):
        mock_db_users_ref.get.return_value = MagicMock()
        with pytest.raises(ResourceAlreadyExistsError):
            create_user(mock_user_id, mock_json_dict)


def test_create_user_when_set_user_fails_raise_firebase_error(app):
    mock_db_users_ref = MagicMock()
    mock_user_id = "test_user"
    mock_first_name = "Test"
    mock_last_name = "User"
    mock_json_dict = {
        "user_id": mock_user_id,
        "first_name": mock_first_name,
        "last_name": mock_last_name
    }

    with patch("firebase_admin.db.reference", return_value=mock_db_users_ref):
        mock_db_users_ref.get.return_value = None
        mock_db_users_ref.set.side_effect = FirebaseError(8, "test")

        with pytest.raises(FirebaseError):
            create_user(mock_user_id, mock_json_dict)


def test_update_user_when_user_is_updated_return_updated_data(app):
    mock_db_users_ref = MagicMock()
    mock_user_id = "test_user"
    mock_first_name = "new fname"
    mock_last_name = "new lname"
    mock_phone = "new phone"
    mock_json_dict = {
        "first_name": mock_first_name,
        "last_name": mock_last_name,
        "phone": mock_phone,
        "Invalid key": "Invalid"
    }
    mock_updated_data = {
        "first_name": mock_first_name,
        "last_name": mock_last_name,
        "phone": mock_phone
    }

    with patch("firebase_admin.db.reference", return_value=mock_db_users_ref):
        mock_db_users_ref.get.return_value = MagicMock()
        mock_db_users_ref.update.return_value = None

        updated_data = update_user(user_id=mock_user_id, user_json_dict=mock_json_dict)
        mock_db_users_ref.update.called_once_with(mock_updated_data)
        assert mock_updated_data == updated_data


def test_update_user_when_user_doesnt_exist_raise_user_not_found_error(app):
    mock_db_users_ref = MagicMock()
    mock_user_id = "test_user"
    mock_first_name = "new fname"
    mock_json_dict = {
        "first_name": mock_first_name,
    }

    with patch("firebase_admin.db.reference", return_value=mock_db_users_ref):
        mock_db_users_ref.get.return_value = None
        with pytest.raises(ResourceNotFoundError):
            update_user(mock_user_id, mock_json_dict)


def test_update_user_when_get_fails_raise_error(app):
    mock_db_users_ref = MagicMock()
    mock_user_id = "test_user"
    mock_first_name = "new fname"
    mock_json_dict = {
        "first_name": mock_first_name,
    }

    with patch("firebase_admin.db.reference", return_value=mock_db_users_ref):
        mock_db_users_ref.get.side_effect = FirebaseError(8, "test")
        with pytest.raises(FirebaseError):
            update_user(mock_user_id, mock_json_dict)


def test_update_user_when_no_valid_update_fields_raise_invalid_request_error(app):
    mock_db_users_ref = MagicMock()
    mock_user_id = "test_user"
    mock_json_dict = {
        "Invalid key": "Invalid"
    }

    with patch("firebase_admin.db.reference", return_value=mock_db_users_ref):
        mock_db_users_ref.get.return_value = MagicMock()
        with pytest.raises(InvalidRequestError):
            update_user(mock_user_id, mock_json_dict)


def test_update_user_when_update_fails_raise_firebase_error(app):
    mock_db_users_ref = MagicMock()
    mock_user_id = "test_user"
    mock_json_dict = {
        "first_name": "new fname",
    }

    with patch("firebase_admin.db.reference", return_value=mock_db_users_ref):
        mock_db_users_ref.get.return_value = MagicMock()
        mock_db_users_ref.update.side_effect = FirebaseError(8, "test")
        with pytest.raises(FirebaseError):
            update_user(mock_user_id, mock_json_dict)
