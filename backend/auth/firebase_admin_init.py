import firebase_admin
from firebase_admin import credentials, auth

# Load Firebase Admin SDK
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
