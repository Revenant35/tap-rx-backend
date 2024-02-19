import os
from unittest.mock import patch

import pytest


@pytest.fixture
def app():
    os.environ["FIREBASE_CREDENTIALS_PATH"] = "test_credentials.json"
    os.environ["FIREBASE_DB_URL"] = "test_db_url"
    from src.app import create_app

    with patch("src.database.firebase_config.initialize_firebase_app"), \
            patch("firebase_admin.credentials.Certificate"), \
            patch("firebase_admin.initialize_app"):
        app = create_app()
        app.config.update({
            "TESTING": True
        })
        with app.app_context():
            yield app
