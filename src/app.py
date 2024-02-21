from flask import Flask

from src.database.firebase_config import initialize_firebase_app
from src.routes.base import base_bp
from src.routes.medication_router import medications_bp
from src.routes.user_router import users_bp


def create_app(test_config=None):
    initialize_firebase_app()

    app = Flask(__name__, instance_relative_config=True)

    if test_config:
        app.config.update(test_config)

    app.register_blueprint(base_bp)
    app.register_blueprint(medications_bp, url_prefix='/medications')
    app.register_blueprint(users_bp, url_prefix='/users')

    return app
