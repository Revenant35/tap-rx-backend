import os
from functools import wraps
from typing import Optional

import firebase_admin
import flask
from dotenv import load_dotenv
from firebase_admin import auth
from flask import request, jsonify, Response, current_app

load_dotenv()


def firebase_auth_required(f):
    """
    Decorator to require Firebase Auth for a route.
    Args:
        f: The function to decorate.

    Notes:
        if FLASK_ENV is set to 'development', this decorator will bypass Firebase Auth.

    Returns:
        The decorated function.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if os.getenv('FLASK_ENV') == 'development':
            return f(*args, **kwargs)

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


def get_user_id(req: flask.Request) -> Optional[str]:
    """
    Retrieves the user ID from the request.

    Args:
        req: (flask.Request) The request object.

    Returns:
        Optional[str]: The user ID if found, otherwise None.
    """
    try:
        return req.decoded_token['user_id']
    except (AttributeError, KeyError, ValueError, TypeError):
        return None


def verify_user(user_id: str, req: flask.Request) -> tuple[bool, Optional[tuple[Response, int]]]:
    """
    Verifies that the user making the request is the same as the user being requested.

    Args:
        user_id: (str) Username for user.
        req: (flask.Request) The request object.

    Notes:
        if FLASK_ENV is set to 'development', this function will bypass Firebase Auth.

    Returns:
        tuple[bool, Optional[tuple[Response, int]]]: A tuple containing a boolean representing whether the user was
        verified and an optional tuple of Response and int representing the error response and status code if there was
        an error.
    """
    if os.getenv('FLASK_ENV') == 'development':
        return True, None

    requesting_user_id = get_user_id(req)

    if requesting_user_id is None or user_id != requesting_user_id:
        current_app.logger.error(f"Insufficient permissions: {requesting_user_id} != {user_id}")
        return False, (jsonify({"message": "Insufficient permissions"}), 403)

    return True, None
