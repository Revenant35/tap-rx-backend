from datetime import datetime
from unittest.mock import patch

from src.models.MedicationEvent import MedicationEvent


def test_handle_get_medication_event_when_medication_is_found_return_200(app, client):
    user_id = "user_id"
    medication_id = "medication_id"
    medication_event_id = "medication_event_id"
    medication_event = MedicationEvent(
        medication_event_id=medication_event_id,
        user_id=user_id,
        medication_id=medication_id,
        timestamp=datetime.now(),
    )

    with patch("src.routes.medication_event_router.get_user_id", return_value=user_id), \
            patch("src.routes.medication_event_router.get_medication_event", return_value=medication_event):
        response = client.get(f"/medications/{medication_id}/events/{medication_event_id}")
        assert response.status_code == 200
        assert response.json["data"] == medication_event.to_dict()


def test_handle_get_medication_event_when_medication_is_not_found_return_404(app, client):
    user_id = "user_id"
    medication_id = "medication_id"
    medication_event_id = "medication_event_id"

    with patch("src.routes.medication_event_router.get_user_id", return_value=user_id), \
            patch("src.routes.medication_event_router.get_medication_event", return_value=None):
        response = client.get(f"/medications/{medication_id}/events/{medication_event_id}")
        assert response.status_code == 404


def test_handle_create_medication_event_when_event_is_created_return_201(app, client):
    user_id = "user_id"
    medication_id = "medication_id"
    medication_event_id = "medication_event_id"
    medication_event = MedicationEvent(
        medication_event_id=medication_event_id,
        user_id=user_id,
        medication_id=medication_id,
        timestamp=datetime.now(),
    )

    with patch("src.routes.medication_event_router.get_user_id", return_value=user_id), \
            patch("src.routes.medication_event_router.create_medication_event", return_value=medication_event):
        response = client.post(f"/medications/{medication_id}/events/", json=medication_event.to_dict())
        assert response.status_code == 201
        assert response.json["data"] == medication_event.to_dict()


def test_handle_update_medication_event_when_event_is_updated_return_200(app, client):
    user_id = "user_id"
    medication_id = "medication_id"
    medication_event_id = "medication_event_id"
    updated_med_event_data = {
        "timestamp": datetime.now().isoformat(),
        "dosage": "dosage"
    }

    with patch("src.routes.medication_event_router.get_user_id", return_value=user_id), \
            patch("src.routes.medication_event_router.update_medication_event", return_value=updated_med_event_data):
        response = client.put(f"/medications/{medication_id}/events/{medication_event_id}", json=updated_med_event_data)
        assert response.status_code == 200
        assert response.json["data"] == updated_med_event_data


def test_handle_delete_medication_event_when_event_is_deleted_return_204(app, client):
    user_id = "user_id"
    medication_id = "medication_id"
    medication_event_id = "medication_event_id"

    with patch("src.routes.medication_event_router.get_user_id", return_value=user_id), \
            patch("src.routes.medication_event_router.delete_medication_event", return_value=None):
        response = client.delete(f"/medications/{medication_id}/events/{medication_event_id}")
        assert response.status_code == 204
