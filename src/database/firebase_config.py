import os

import firebase_admin
from dotenv import load_dotenv
from firebase_admin import credentials

FIREBASE_CREDENTIALS_PATH = "FIREBASE_CREDENTIALS_PATH"
FIREBASE_DB_URL = "FIREBASE_DB_URL"

load_dotenv()

if os.getenv(FIREBASE_CREDENTIALS_PATH) is None:
    raise ValueError("FIREBASE_CREDENTIALS_PATH environment variable is not set")
if os.getenv(FIREBASE_DB_URL) is None:
    raise ValueError("FIREBASE_DB_URL environment variable is not set")


def initialize_firebase_app() -> None:
    if firebase_admin._apps:
        raise ValueError("Firebase app already initialized")

    cred = credentials.Certificate(os.getenv(FIREBASE_CREDENTIALS_PATH))
    firebase_admin.initialize_app(cred, {"databaseURL": os.getenv(FIREBASE_DB_URL)})
