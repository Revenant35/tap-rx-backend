import yaml
from flasgger import Swagger
from flask import Flask

from src.database.firebase_config import initialize_firebase_app
from src.models.errors.error_handlers import register_error_handlers
from src.routes.base import base_bp
from src.routes.dependant_router import dependant_bp
from src.routes.medication_event_router import medication_events_bp
from src.routes.medication_router import medications_bp
from src.routes.user_router import users_bp


def read_yaml_file(file_path: str):
    """
    Reads a YAML file and returns its contents.
    Args:
        file_path: (str) The path to the YAML file.

    Returns:
        dict: The contents of the YAML file.
    """
    with open(file_path, "r") as file:
        return yaml.safe_load(file)


def init_swagger(app: Flask):
    """
    Initializes the Swagger UI for the Flask app.

    Args:
        app: (Flask) The Flask app to initialize Swagger for.
    """
    models = read_yaml_file("src/documentation/models.yaml")
    swagger_config = {
        "title": "TapRx API",
        "version": "0.1.0",
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec_1",
                "route": "/apispec_1.json",
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/apidocs/",
        "definitions": models,  # Add your loaded models here
    }
    swagger = Swagger(app, config=swagger_config)


def create_app():
    initialize_firebase_app()

    app = Flask(__name__, instance_relative_config=True)
    init_swagger(app)

    app.register_blueprint(base_bp)
    app.register_blueprint(medications_bp, url_prefix="/medications")
    app.register_blueprint(users_bp, url_prefix="/users")
    app.register_blueprint(medication_events_bp, url_prefix="/medications")
    app.register_blueprint(dependant_bp)
    register_error_handlers(app)

    return app
