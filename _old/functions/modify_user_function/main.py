import json
import logging
import os

import firebase_admin
import jwt
import requests
from firebase_admin import _apps, credentials, exceptions, auth, firestore, initialize_app
from flask import Flask, request, abort, jsonify
import functions_framework
from firebase_admin import db


if not firebase_admin._apps:
    cred = firebase_admin.credentials.Certificate("taprx-9c82f-firebase-adminsdk-4qccq-14a61c165f.json")
    firebase_admin.initialize_app(cred)

MAX_FIRST_NAME_LENGTH = 64
MAX_LAST_NAME_LENGTH = 64
MAX_PHONE_LENGTH = 64

uid = 'BZSnmi2eSCWHLmDcYxlD6xhhDfK2'
custom_token = auth.create_custom_token(uid)
token = custom_token.decode('utf-8')
print(token)
# curl "https://<DATABASE_NAME>.firebaseio.com/users/ada/name.json?auth=<ID_TOKEN>"
# x = requests.get('https://taprx-9c82f-default-rtdb.firebaseio.com/users/ada/name.json?auth=' + decoded_token)

# Function to verify Firebase ID token
def verify_token(req: request) -> dict:
    authorization_header = req.headers.get('Authorization')
    if not authorization_header:
        abort(401, 'Authorization header is missing')

    id_token = authorization_header.split('Bearer ')[1]

    try:
        # decoded_token = auth.verify_id_token(id_token)
        decoded_token = {
            "uid": "test"
        }
        return decoded_token
    except Exception as e:
        logging.error(f'Error verifying Firebase ID token: {e}')
        abort(403, 'Invalid or expired Firebase ID token')


@functions_framework.http
def modify_user_handler(user_id: int):
    """
    Modifies an existing user in the Firebase Realtime Database. Uses the Firebase Admin SDK to interact with the database.
    Args:
        user_id (int): The ID of the user to modify.
        req (request): The request object.

    Returns:
        Response that can be converted into a flask.Response object.
    """

    try:
        # Verify Firebase ID token and extract UID
        user = verify_token(request)
    except Exception as e:
        logging.error(f'Error verifying Firebase ID token: {e}')
        abort(403, 'Invalid or expired Firebase ID token')

    if user['uid'] != user_id:
        logging.error(f'User {user["uid"]} does not have permission to modify user {user_id}')
        abort(403, 'Insufficient permissions')

    try:
        # Get the body of the request
        username = request.form.get("username")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        phone = request.form.get("phone")
    except (ValueError, TypeError, KeyError) as ex:
        logging.error(f"Invalid request JSON: {ex}")
        abort(400, "Invalid request")

    if username and len(username) > MAX_USERNAME_LENGTH:
        abort(400, f"Username must be less than {MAX_USERNAME_LENGTH} characters")
    if first_name and len(first_name) > MAX_FIRST_NAME_LENGTH:
        abort(400, f"First name must be less than {MAX_FIRST_NAME_LENGTH} characters")
    if last_name and len(last_name) > MAX_LAST_NAME_LENGTH:
        abort(400, f"Last name must be less than {MAX_LAST_NAME_LENGTH} characters")
    if phone and len(phone) > MAX_PHONE_LENGTH:
        abort(400, f"Phone number must be less than {MAX_PHONE_LENGTH} characters")

    print(username, first_name, last_name, phone)

    # db = firestore.client()
    # user_ref = db.collection('users').document(user['uid'])

    # user_updates = {
    #     "username": username,
    #     "first_name": first_name,
    #     "last_name": last_name,
    #     "email": email,
    #     "phone": phone
    # }

    try:
        # Update the user's document with provided information
        # user_ref.update(user_updates)
        return jsonify({"message": "User information updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": "Failed to update user information", "details": str(e)}), 500


    #
    # try:
    #     request_json = request.get_json(silent=True)
    #     username = request_json["username"]
    #     first_name = request_json["first_name"]
    #     last_name = request_json["last_name"]
    #     email = request_json["email"]
    #     phone = request_json["phone"]
    # except (ValueError, TypeError, KeyError) as ex:
    #     logging.error(f"Invalid request JSON: {ex}")
    #     return "Invalid request", 400

    # try:
    #     firebase_key_dict = json.loads(get_env_var(FIREBASE_KEY))
    # except json.JSONDecodeError as ex:
    #     logging.error(f"JSON decoding error when decoding the firebase key: {ex}")
    #     return "Internal server error", 500
    # except ValueError:
    #     return "Internal server error", 500
    #
    # try:
    #     firebase_db_url = get_env_var(FIREBASE_DATABASE_URL)
    # except ValueError:
    #     return "Internal server error", 500
    #
    # try:
    #     register_user.initialize_firebase_app(firebase_key_dict, firebase_db_url)
    # except (ValueError, IOError):
    #     return "Internal server error", 500
    #
    # try:
    #     db_users_ref = db.reference("/users")
    # except ValueError as ex:
    #     logging.error(f"Invalid database reference: {ex}")
    #     return "Internal server error", 500
    #
    # try:
    #     register_user.store_user(db_users_ref, username, first_name, last_name, email, phone)
    # except (ValueError, TypeError, firebase_admin.exceptions.FirebaseError):
    #     return "Internal server error", 500
    # except register_user.UserAlreadyExistsError:
    #     return "User already exists", 409
    #
    # return "OK", 200


# def get_env_var(env_var_name: str) -> str:
#     """
#     Retrieve the value of the specified environment variable.
#
#     Parameters:
#     - env_var_name (str): The name of the environment variable to retrieve.
#
#     Returns:
#     - str: The value of the environment variable.
#
#     Raises:
#     - ValueError: If the environment variable is not set or if the var parameter is None.
#     """
#     if not env_var_name:
#         logging.error(f"The environment variable name is None")
#         raise ValueError("The environment variable name is None.")
#
#     env_var = os.environ.get(env_var_name)
#     if not env_var:
#         logging.error(f"The environment variable {env_var_name} is not set.")
#         raise ValueError(f"The environment variable {env_var_name} is not set.")
#     return env_var

# For local testing
if __name__ == '__main__':
    app = Flask(__name__)

    @app.route('/<user_id>', methods=['PUT'])
    def local_test(user_id: int):
        return modify_user_handler(user_id)

    app.run(port=8080, debug=True)
