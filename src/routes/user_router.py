from flask import Blueprint, jsonify
from src.routes.auth import firebase_auth_required

users_bp = Blueprint('users_bp', __name__)


@users_bp.route('/', methods=['GET'])
def get_users():
    return jsonify({"message": "Listing all users"}), 200


@users_bp.route('/<user_id>', methods=['GET'])
@firebase_auth_required
def get_user(user_id):
    return jsonify({"message": f"Retrieving user {user_id}"}), 200
