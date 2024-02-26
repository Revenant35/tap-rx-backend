from firebase_admin.exceptions import FirebaseError
from flask import jsonify

from src.models.errors.invalid_request_error import InvalidRequestError
from src.models.errors.resource_not_found_error import ResourceNotFoundError
from src.models.errors.resource_already_exists_error import ResourceAlreadyExistsError


def register_error_handlers(app):

    @app.errorhandler(InvalidRequestError)
    def handle_invalid_request_error(e):
        return jsonify({
            "success": False,
            "message": "Invalid request",
            "error": e.message
        }), 400

    @app.errorhandler(ResourceNotFoundError)
    def handle_resource_not_found_error(e):
        return jsonify({
            "success": False,
            "message": "Resource not found",
            "error": e.message
        }), 404

    @app.errorhandler(ResourceAlreadyExistsError)
    def handle_resource_already_exists_error(e):
        return jsonify({
            "success": False,
            "message": "Resource already exists",
            "error": e.message
        }), 409

    @app.errorhandler(FirebaseError)
    def handle_firebase_error(e):
        return jsonify({
            "success": False,
            "message": "Internal server error"
        }), 500
