import firebase_admin
from firebase_admin import credentials
import os
from dotenv import load_dotenv

load_dotenv()

if os.getenv('FIREBASE_CREDENTIALS_PATH') is None:
    raise ValueError("FIREBASE_CREDENTIALS_PATH environment variable is not set")


def initialize_firebase_app():
    if firebase_admin._apps:
        raise ValueError("Firebase app already initialized")
    credentials_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
    cred = credentials.Certificate(credentials_path)
    firebase_admin.initialize_app(cred)
    print("Firebase app initialized")
