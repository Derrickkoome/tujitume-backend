from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from typing import Generator, Optional
import firebase_admin
from firebase_admin import credentials, auth
import os


# Initialize Firebase Admin (only once)
if not firebase_admin._apps:
    # Try JSON from environment variable first (for Render/cloud platforms)
    firebase_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
    if firebase_json:
        import json
        try:
            cred_dict = json.loads(firebase_json)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            print("Firebase initialized from environment variable")
        except Exception as e:
            print(f"Failed to initialize Firebase from JSON env var: {e}")
    # Check if running with service account file path
    elif os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH"):
        cred_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            print(f"Firebase initialized from file: {cred_path}")
    else:
        # Development mode - use default credentials or application default
        try:
            firebase_admin.initialize_app()
            print("Firebase initialized with default credentials")
        except Exception as e:
            print(f"Warning: Firebase not initialized: {e}")
            print("Firebase auth will not work without proper credentials")


# Security
security = HTTPBearer()


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> dict:
    """
    Verify Firebase token and return user info.
    Creates user in database if doesn't exist.
    """
    token = credentials.credentials
    
    try:
        # Verify the Firebase ID token
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token['uid']
        email = decoded_token.get('email')
        name = decoded_token.get('name')
        
        # Get or create user in database
        from app.crud import crud
        user = crud.get_or_create_user(db, uid=uid, email=email, name=name)
        
        return {
            "uid": uid,
            "email": email,
            "name": name,
            "db_user": user
        }
    except auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )
    except auth.ExpiredIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token has expired"
        )
    except Exception as e:
        print(f"Auth error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


async def verify_firebase_token(token: str) -> dict:
    """
    Verify Firebase ID token and return decoded token.
    Raises HTTPException if token is invalid.
    """
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )
    except auth.ExpiredIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token has expired"
        )
    except Exception as e:
        print(f"Token verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[dict]:
    """
    Optional authentication - returns None if no token provided
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None
