import logging
import flask
import functions_framework
from firebase_admin import auth, credentials, initialize_app, db
import firebase_admin

# Initialize Firebase Admin SDK if it hasn't been initialized
if not firebase_admin._apps:
    cred = credentials.Certificate("path/to/your/serviceAccountKey.json")
    default_app = initialize_app(cred, {
        'databaseURL': 'https://your-database-url.firebaseio.com/'
    })


# Function to verify Firebase ID token
def verify_firebase_id_token(request):
    authorization_header = request.headers.get('Authorization')
    if not authorization_header:
        flask.abort(401, 'Authorization header is missing')

    id_token = authorization_header.split('Bearer ')[1]
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        logging.error(f'Error verifying Firebase ID token: {e}')
        flask.abort(403, 'Invalid or expired Firebase ID token')


@functions_framework.http
def example_function(request: flask.Request):
    """
    Demonstrates how to verify a user's ID before returning secure data.
    """
    # Verify Firebase ID Token
    user = verify_firebase_id_token(request)

    requested_user_id = request.view_args['user_id']
    requester_user_id = user['uid']

    if requested_user_id != requester_user_id:
        flask.abort(403, 'Insufficient permissions')

    # Proceed with the registration logic if the token is valid

    return flask.jsonify({"message": "Function executed successfully", "user": user})
