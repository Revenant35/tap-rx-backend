from functools import wraps
from flask import request, jsonify
import firebase_admin
from firebase_admin import auth


def firebase_auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not firebase_admin._apps:
            raise ValueError("Firebase app is not initialized")

        if 'Authorization' not in request.headers:
            return jsonify({"message": "Authorization header is missing"}), 401

        split_token = request.headers['Authorization'].split(' ')
        if len(split_token) != 2 or split_token[0] != 'Bearer' or not split_token[1]:
            return jsonify({"message": "Invalid token format"}), 400

        id_token = split_token[1]

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
