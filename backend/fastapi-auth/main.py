from fastapi import FastAPI, Header, HTTPException
import firebase_admin
from firebase_admin import auth as firebase_auth, credentials
import os

app = FastAPI()

# Initialize Firebase Admin with a service account JSON file path from env
FIREBASE_CRED = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
if FIREBASE_CRED and os.path.exists(FIREBASE_CRED):
    cred = credentials.Certificate(FIREBASE_CRED)
    firebase_admin.initialize_app(cred)
else:
    # If no service account provided, admin SDK will attempt default credentials
    try:
        firebase_admin.initialize_app()
    except Exception:
        # Not initialized; verify will fail until proper credentials are provided
        pass


@app.post('/api/auth/session')
async def create_session(authorization: str | None = Header(None)):
    """Accepts a Bearer ID token from the client and verifies it with Firebase."""
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail='Missing token')
    id_token = authorization.split(' ', 1)[1]
    try:
        decoded = firebase_auth.verify_id_token(id_token)
        uid = decoded.get('uid')
        return {'uid': uid, 'decoded': decoded}
    except Exception as e:
        raise HTTPException(status_code=401, detail=f'Invalid token: {e}')
