from flask import Flask
from src.database.firebase_config import initialize_firebase_app

# Routes
from src.routes.base import base_bp
from src.routes.user_router import users_bp


def create_app(test_config=None):
    initialize_firebase_app()

    app = Flask(__name__, instance_relative_config=True)

    if test_config:
        app.config.update(test_config)

    app.register_blueprint(base_bp)
    app.register_blueprint(users_bp, url_prefix='/users')

    return app


app = create_app()
