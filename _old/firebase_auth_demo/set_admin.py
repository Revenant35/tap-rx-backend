import firebase_admin
from firebase_admin import auth


# Initialize the Firebase app if not already initialized
if not firebase_admin._apps:
    firebase_admin.initialize_app()


def set_admin_privileges(uid):
    # Set custom user claims on this user.
    auth.set_custom_user_claims(uid, {'admin': True})


# Replace 'some-uid' with the UID of the user you want to make an admin
set_admin_privileges('some-uid')
