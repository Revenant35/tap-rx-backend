import os
from unittest.mock import MagicMock
from src.routes.auth import verify_user, get_user_id
import pytest


@pytest.fixture(autouse=True)
def env_setup_and_teardown():
    # Save the original value of FLASK_ENV
    original_flask_env = os.getenv('FLASK_ENV')

    # This code runs before each test
    yield

    # This code runs after each test
    if original_flask_env is None:
        os.unsetenv('FLASK_ENV')  # Unset if it was not set before
    else:
        os.environ['FLASK_ENV'] = original_flask_env  # Reset to original value


# get_user_id()
def test_get_user_id_called_with_valid_request_returns_user_id(app):
    mock_request = MagicMock()
    mock_request.decoded_token = {"user_id": "test_user"}

    user_id = get_user_id(mock_request)
    assert user_id == "test_user"


def test_get_user_id_called_with_no_decoded_token_returns_none(app):
    mock_request = MagicMock()
    mock_request.decoded_token = None

    user_id = get_user_id(mock_request)
    assert user_id is None


def test_get_user_id_called_with_no_user_id_in_decoded_token_returns_none(app):
    mock_request = MagicMock()
    mock_request.decoded_token = {"other_key": "test_value"}

    user_id = get_user_id(mock_request)
    assert user_id is None


def test_get_user_id_called_with_non_dict_decoded_token_returns_none(app):
    mock_request = MagicMock()
    mock_request.decoded_token = "non_dict_value"

    user_id = get_user_id(mock_request)
    assert user_id is None


# verify_user()
def test_verify_user_called_in_development_environment_returns_true_and_none(app):
    mock_user_id = "test_user"
    os.environ['FLASK_ENV'] = 'development'
    mock_request = MagicMock()
    mock_request.decoded_token = {"user_id": mock_user_id}

    verified, error_response = verify_user(mock_user_id, mock_request)
    assert verified is True
    assert error_response is None


def test_verify_user_called_with_same_user_id_returns_true_and_none(app):
    mock_user_id = "test_user"
    os.environ['FLASK_ENV'] = 'production'
    mock_request = MagicMock()
    mock_request.decoded_token = {"user_id": mock_user_id}

    verified, error_response = verify_user(mock_user_id, mock_request)
    assert verified is True
    assert error_response is None


def test_verify_user_called_with_different_user_id_returns_false_and_403(app):
    os.environ['FLASK_ENV'] = 'production'
    mock_request = MagicMock()
    mock_request.decoded_token = {"user_id": "test_user"}

    verified, error_response = verify_user("other_user", mock_request)
    assert verified is False
    assert error_response[1] == 403


def test_verify_user_called_with_no_decoded_token_returns_false_and_403(app):
    os.environ['FLASK_ENV'] = 'production'
    mock_request = MagicMock()
    mock_request.decoded_token = None

    verified, error_response = verify_user("test_user", mock_request)
    assert verified is False
    assert error_response[1] == 403
