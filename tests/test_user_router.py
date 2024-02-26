from unittest.mock import patch, MagicMock

from firebase_admin.exceptions import FirebaseError
from flask import jsonify

from src.models.errors.invalid_request_error import InvalidRequestError
from src.models.errors.resource_already_exists_error import ResourceAlreadyExistsError
from src.models.errors.resource_not_found_error import ResourceNotFoundError


def test_handle_create_user_when_user_is_created_return_201(app, client):

    mock_user_data = {
        "user_id": "test_user",
        "first_name": "test",
        "last_name": "user",
    }
    mock_user = MagicMock()
    mock_user.to_dict.return_value = mock_user_data

    with patch("src.routes.user_router.verify_user", return_value=(True, None)), \
            patch("src.routes.user_router.create_user", return_value=mock_user):
        response = client.post("/users/", json=mock_user_data)
        assert response.status_code == 201
        assert response.json["success"] is True
        assert response.json["message"] == "User created successfully"
        assert response.json["data"] == mock_user_data


def test_handle_create_user_when_user_id_is_missing_return_400(app, client):
    mock_user_data = {
        "first_name": "test",
    }

    response = client.post("/users/", json=mock_user_data)
    assert response.status_code == 400


def test_handle_create_user_when_user_is_not_verified_return_403(app, client):
    mock_user_data = {
        "user_id": "test_user",
        "first_name": "test",
        "last_name": "user",
    }
    error_response = jsonify({"message": "Insufficient permissions"})

    with patch("src.routes.user_router.verify_user", return_value=(False, (error_response, 403))):
        response = client.post("/users/", json=mock_user_data)
        assert response.status_code == 403


def test_handle_create_user_when_invalid_user_data_return_400(app, client):
    mock_user_data = {
        "user_id": "test_user",
        "invalid_key": "invalid value"
    }

    with patch("src.routes.user_router.verify_user", return_value=(True, None)), \
            patch("src.routes.user_router.create_user", side_effect=InvalidRequestError):
        response = client.post("/users/", json=mock_user_data)
        assert response.status_code == 400


def test_handle_create_user_when_user_already_exists_return_409(app, client):
    mock_user_data = {
        "user_id": "test_user",
        "first_name": "test",
        "last_name": "user"
    }

    with patch("src.routes.user_router.verify_user", return_value=(True, None)), \
            patch("src.routes.user_router.create_user", side_effect=ResourceAlreadyExistsError):
        response = client.post("/users/", json=mock_user_data)
        assert response.status_code == 409


def test_handle_create_user_when_user_cant_be_created_return_500(app, client):
    mock_user_data = {
        "user_id": "test_user",
        "first_name": "test",
        "last_name": "user"
    }

    with patch("src.routes.user_router.verify_user", return_value=(True, None)), \
            patch("src.routes.user_router.create_user", side_effect=FirebaseError(8, "test")):
        response = client.post("/users/", json=mock_user_data)
        assert response.status_code == 500


def test_handle_update_user_when_user_is_updated_return_200(app, client):
    mock_user_id = "test_user"
    mock_user_data = {
        "last_name": "new user",
        "invalid_key": "invalid value"
    }
    mock_updated_data = {
        "last_name": "new user",
    }

    with patch("src.routes.user_router.verify_user", return_value=(True, None)), \
            patch("src.routes.user_router.update_user", return_value=mock_updated_data):
        response = client.put(f"/users/{mock_user_id}", json=mock_user_data)
        assert response.status_code == 200
        assert response.json["success"] is True
        assert response.json["message"] == "User updated"
        assert response.json["data"] == mock_updated_data


def test_handle_update_user_when_user_is_not_verified_return_403(app, client):
    mock_user_id = "test_user"
    mock_user_data = {
        "last_name": "new user"
    }
    error_response = jsonify({"message": "Insufficient permissions"})

    with patch("src.routes.user_router.verify_user", return_value=(False, (error_response, 403))):
        response = client.put(f"/users/{mock_user_id}", json=mock_user_data)
        assert response.status_code == 403


def test_handle_update_user_when_user_doesnt_exist_return_404(app, client):
    mock_user_id = "test_user"
    mock_user_data = {
        "last_name": "new user"
    }

    with patch("src.routes.user_router.verify_user", return_value=(True, None)), \
            patch("src.routes.user_router.update_user", side_effect=ResourceNotFoundError("User not found")):
        response = client.put(f"/users/{mock_user_id}", json=mock_user_data)
        assert response.status_code == 404


def test_handle_update_user_when_user_cant_be_updated_return_500(app, client):
    mock_user_id = "test_user"
    mock_user_data = {
        "last_name": "new user"
    }

    with patch("src.routes.user_router.verify_user", return_value=(True, None)), \
            patch("src.routes.user_router.update_user", side_effect=FirebaseError(8, "test")):
        response = client.put(f"/users/{mock_user_id}", json=mock_user_data)
        assert response.status_code == 500
