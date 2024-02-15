from functools import wraps
from typing import Optional

import firebase_admin
import flask
from firebase_admin import auth
from flask import request, jsonify, Response, current_app


def firebase_auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not firebase_admin._apps:
            raise ValueError("Firebase app is not initialized")

        if 'Authorization' not in request.headers:
            return jsonify({"message": "Authorization header is missing"}), 401

        id_token = request.headers['Authorization']

        try:
            decoded_token = auth.verify_id_token(id_token)
            request.decoded_token = decoded_token
        except auth.ExpiredIdTokenError:
            return jsonify({"message": "ID token has expired"}), 403
        except auth.RevokedIdTokenError:
            return jsonify({"message": "ID token has been revoked"}), 403
        except auth.InvalidIdTokenError:
            return jsonify({"message": "Invalid ID token"}), 403

        return f(*args, **kwargs)
    return decorated_function


def verify_user(user_id: str, request: flask.Request) -> tuple[bool, Optional[tuple[Response, int]]]:
    """
    Verifies that the user making the request is the same as the user being requested.

    Args:
        user_id: (str) Username for user.
        request: (flask.Request) The request object.

    Returns:
        bool: True if the user is verified, otherwise False.
    """
    try:
        requesting_user_id = request.decoded_token['user_id']
    except (AttributeError, KeyError, ValueError) as ex:
        current_app.logger.error(f"Invalid request JSON: {ex}")
        return False, (jsonify({"message": "Invalid request"}), 400)

    if user_id != requesting_user_id:
        current_app.logger.error(f"Insufficient permissions: {requesting_user_id} != {user_id}")
        return False, (jsonify({"message": "Insufficient permissions"}), 403)
    else:
        return True, None
