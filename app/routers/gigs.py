from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.schemas import schemas
from app.crud import crud
from app.core.dependencies import get_db, get_current_user, get_current_user_optional


router = APIRouter(prefix="/api/gigs", tags=["gigs"])


@router.get("/", response_model=List[schemas.GigResponse])
def list_gigs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    sort_by: str = Query("created_at", regex="^(created_at|budget)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    budget_type: Optional[str] = Query(None, regex="^(fixed|hourly)$"),
    skills: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get all gigs with optional filtering and sorting.
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **sort_by**: Field to sort by (created_at or budget)
    - **sort_order**: Sort order (asc or desc)
    - **budget_type**: Filter by budget type (fixed or hourly)
    - **skills**: Comma-separated list of skills to filter by
    - **search**: Search in title, description, or location
    """
    # Parse skills if provided
    skills_list = None
    if skills:
        skills_list = [s.strip() for s in skills.split(",") if s.strip()]
    
    gigs = crud.get_gigs(
        db=db,
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order,
        budget_type=budget_type,
        skills=skills_list,
        search=search
    )
    return gigs


@router.get("/{gig_id}", response_model=schemas.GigResponse)
def get_gig(
    gig_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific gig by ID.
    """
    gig = crud.get_gig(db, gig_id)
    if not gig:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gig not found"
        )
    return gig


@router.post("/", response_model=schemas.GigResponse, status_code=status.HTTP_201_CREATED)
def create_gig(
    gig: schemas.GigCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new gig. Requires authentication.
    """
    return crud.create_gig(db=db, gig=gig, owner_id=current_user["uid"])


@router.put("/{gig_id}", response_model=schemas.GigResponse)
def update_gig(
    gig_id: int,
    gig_update: schemas.GigUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a gig. Only the owner can update their gig.
    """
    existing_gig = crud.get_gig(db, gig_id)
    if not existing_gig:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gig not found"
        )
    
    # Check if current user is the owner
    if existing_gig.owner_id != current_user["uid"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this gig"
        )
    
    updated_gig = crud.update_gig(db, gig_id, gig_update)
    return updated_gig


@router.delete("/{gig_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_gig(
    gig_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a gig. Only the owner can delete their gig.
    """
    existing_gig = crud.get_gig(db, gig_id)
    if not existing_gig:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gig not found"
        )
    
    # Check if current user is the owner
    if existing_gig.owner_id != current_user["uid"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this gig"
        )
    
    crud.delete_gig(db, gig_id)
    return None


@router.post("/{gig_id}/apply", response_model=schemas.ApplicationResponse, status_code=status.HTTP_201_CREATED)
def apply_to_gig(
    gig_id: int,
    application: schemas.ApplicationCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Apply to a gig. Requires authentication.
    Cannot apply to your own gig or apply twice.
    """
    # Check if gig exists
    gig = crud.get_gig(db, gig_id)
    if not gig:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gig not found"
        )
    
    # Check if user is trying to apply to their own gig
    if gig.owner_id == current_user["uid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot apply to your own gig"
        )
    
    # Check if already applied
    existing_application = crud.check_existing_application(db, gig_id, current_user["uid"])
    if existing_application:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already applied to this gig"
        )
    
    # Create application
    return crud.create_application(
        db=db,
        application=application,
        gig_id=gig_id,
        applicant_id=current_user["uid"]
    )


@router.get("/{gig_id}/applications", response_model=List[schemas.ApplicationResponse])
def get_gig_applications(
    gig_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all applications for a gig. Only the gig owner can view applications.
    """
    gig = crud.get_gig(db, gig_id)
    if not gig:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gig not found"
        )
    
    # Check if current user is the owner
    if gig.owner_id != current_user["uid"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view applications for this gig"
        )
    
    return crud.get_gig_applications(db, gig_id)
