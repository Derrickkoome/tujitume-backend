from fastapi import Header, HTTPException
from firebase_admin import auth

async def verify_firebase_token(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid auth scheme")

        decoded = auth.verify_id_token(token)
        return decoded

    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
