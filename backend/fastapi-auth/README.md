FastAPI example: Verify Firebase ID tokens

This folder contains a minimal FastAPI app that verifies Firebase ID tokens sent from the frontend.

Setup
1. Create or obtain a Firebase service account JSON file from Firebase Console → Project settings → Service accounts → Generate new private key.
2. Save that JSON somewhere on your server (do NOT commit it to git).
3. Set the environment variable before starting the app:

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/serviceAccountKey.json
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Endpoint
 - `POST /api/auth/session` — expects an `Authorization: Bearer <ID_TOKEN>` header. The endpoint verifies the token and returns decoded token info (uid etc.).

Security
 - Use HTTPS in production.
 - Restrict who can call this endpoint and create server-side sessions after verification.
