from unittest.mock import MagicMock

from src.routes.auth import verify_user


def test_verify_user_when_user_is_verified_return_true_and_none(app):
    mock_user_id = "test_user"
    mock_request = MagicMock()
    mock_request.decoded_token = {"user_id": mock_user_id}

    verified, error_response = verify_user(mock_user_id, mock_request)
    assert verified is True
    assert error_response is None


def test_verify_user_when_request_not_valid_return_false_and_400(app):
    mock_user_id = "test_user"
    mock_request = MagicMock()
    mock_request.decoded_token = None

    verified, error_response = verify_user(mock_user_id, mock_request)
    assert verified is False
    assert error_response[1] == 400


def test_verify_user_when_user_is_not_verified_return_false_and_403(app):
    mock_user_id = "test_user"
    mock_request = MagicMock()
    mock_request.decoded_token = {"user_id": "other_user"}

    verified, error_code = verify_user(mock_user_id, mock_request)
    assert verified is False
    assert error_code[1] == 403
