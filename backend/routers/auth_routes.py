from fastapi import APIRouter, HTTPException, Depends
from firebase_admin import auth
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["Auth"])

class FirebaseToken(BaseModel):
    token: str

@router.post("/verify-token")
async def verify_firebase_token(data: FirebaseToken):
    try:
        decoded = auth.verify_id_token(data.token)
        return {
            "uid": decoded.get("uid"),
            "email": decoded.get("email")
        }
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid Firebase token")
