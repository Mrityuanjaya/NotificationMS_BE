from firebase_admin import credentials, initialize_app
from apps.libs import firebase


def setup(firebase_service_account_cred):
    if firebase_service_account_cred:
        firebase.FIREBASE_ADMIN_APP = initialize_app(credentials.Certificate(
            "./service_account.json"
        ))