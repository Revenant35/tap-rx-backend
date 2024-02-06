from flask import Blueprint, jsonify

base_bp = Blueprint('base_bp', __name__)


@base_bp.route('/', methods=['GET'])
def get_base():
    return jsonify({"message": "Success"}), 200
