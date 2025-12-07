from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.schemas import schemas
from app.crud import crud
from app.core.dependencies import get_db, get_current_user


router = APIRouter(prefix="/api/users", tags=["users"])


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


@router.get("/me/applications", response_model=List[schemas.ApplicationResponse])
def get_my_applications(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all applications submitted by the current user.
    """
    return crud.get_user_applications(db, current_user["uid"])
