from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from app.schemas import schemas
from app.crud import crud
from app.core.dependencies import get_db, get_current_user, verify_firebase_token


router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: schemas.UserCreate,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Register/sync user from Firebase to database.
    Creates user if doesn't exist, returns existing user if already registered.
    """
    # Verify Firebase token
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    
    token = authorization.split('Bearer ')[1]
    decoded_token = await verify_firebase_token(token)
    uid = decoded_token['uid']
    
    # Check if user already exists
    existing_user = crud.get_user(db, uid)
    if existing_user:
        return existing_user
    
    # Create new user
    new_user = crud.create_user(db, user_data, uid)
    return new_user


@router.get("/me", response_model=schemas.UserResponse)
def get_current_user_info(
    current_user: dict = Depends(get_current_user)
):
    """
    Get current authenticated user's information.
    """
    return current_user["db_user"]


@router.get("/{uid}", response_model=schemas.UserResponse)
def get_user(
    uid: str,
    db: Session = Depends(get_db)
):
    """
    Get user information by UID.
    """
    user = crud.get_user(db, uid)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.get("/me/gigs", response_model=List[schemas.GigResponse])
def get_my_gigs(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all gigs created by the current user.
    """
    return crud.get_user_gigs(db, current_user["uid"])


@router.get("/me/applications", response_model=List[schemas.ApplicationWithDetails])
def get_my_applications(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all applications submitted by the current user with gig details.
    """
    return crud.get_user_applications_with_details(db, current_user["uid"])


@router.put("/me", response_model=schemas.UserResponse)
def update_my_profile(
    user_update: schemas.UserUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's profile information.
    """
    updated_user = crud.update_user(db, current_user["uid"], user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return updated_user
