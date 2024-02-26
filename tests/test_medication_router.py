from unittest.mock import MagicMock, patch

from firebase_admin.exceptions import FirebaseError
from flask import jsonify

from src.models.errors.invalid_request_error import InvalidRequestError
from src.models.errors.resource_not_found_error import ResourceNotFoundError


def test_handle_create_medication_when_medication_is_created_return_201(app, client):
    user_id = "test_user"
    medication_name = "test_medication"
    medication_id = "test_medication_id"
    mock_request_data = {
        "user_id": user_id,
        "medication_name": medication_name
    }
    mock_medication_data = {
        "user_id": user_id,
        "medication_name": medication_name,
        "medication_id": medication_id
    }
    mock_medication = MagicMock()
    mock_medication.to_dict.return_value = mock_medication_data

    with patch("src.routes.medication_router.verify_user", return_value=(True, None)), \
            patch("src.routes.medication_router.create_medication", return_value=mock_medication):
        response = client.post("/medications/", json=mock_request_data)
        assert response.status_code == 201
        assert response.json["success"] is True
        assert response.json["message"] == "Medication created successfully"
        assert response.json["data"] == mock_medication_data


def test_handle_create_user_when_user_id_is_missing_return_400(app, client):
    mock_request_data = {
        "medication_name": "test_medication",
    }

    response = client.post("/users/", json=mock_request_data)
    assert response.status_code == 400


def test_handle_create_medication_when_user_is_not_verified_return_403(app, client):
    mock_request_data = {
        "user_id": "test_user",
        "medication_name": "test_medication",
    }
    error_response = jsonify({"message": "Insufficient permissions"})

    with patch("src.routes.medication_router.verify_user", return_value=(False, (error_response, 403))):
        response = client.post("/medications/", json=mock_request_data)
        assert response.status_code == 403


def test_handle_create_medication_when_invalid_medication_data_return_400(app, client):
    mock_request_data = {
        "user_id": "test_user",
    }

    with patch("src.routes.medication_router.verify_user", return_value=(True, None)), \
            patch("src.routes.medication_router.create_medication", side_effect=InvalidRequestError):
        response = client.post("/medications/", json=mock_request_data)
        assert response.status_code == 400


def test_handle_create_medication_when_user_doesnt_exist_return_404(app, client):
    mock_request_data = {
        "user_id": "test_user",
        "medication_name": "test_medication",
    }

    with patch("src.routes.medication_router.verify_user", return_value=(True, None)), \
            patch("src.routes.medication_router.create_medication", side_effect=ResourceNotFoundError):
        response = client.post("/medications/", json=mock_request_data)
        assert response.status_code == 404


def test_handle_create_medication_when_medication_fails_to_be_created_return_500(app, client):
    mock_request_data = {
        "user_id": "test_user",
        "medication_name": "test_medication",
    }

    with patch("src.routes.medication_router.verify_user", return_value=(True, None)), \
            patch("src.routes.medication_router.create_medication", side_effect=FirebaseError(8, "Test")):
        response = client.post("/medications/", json=mock_request_data)
        assert response.status_code == 500
