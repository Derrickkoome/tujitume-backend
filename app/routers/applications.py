from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict
from app.core.dependencies import get_db, get_current_user
from app.crud import crud
from app.schemas import schemas

router = APIRouter(
    prefix="/api/applications",
    tags=["applications"]
)


@router.put("/{application_id}/select", response_model=schemas.ApplicationResponse)
def select_applicant(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Select an applicant for a gig (accept their application).
    Only the gig owner can select applicants.
    Only one applicant can be selected per gig.
    """
    # Get the application
    application = crud.get_application(db, application_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Get the gig
    gig = crud.get_gig(db, application.gig_id)
    if not gig:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gig not found"
        )
    
    # Check if user is the gig owner
    if gig.owner_id != current_user["uid"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the gig owner can select applicants"
        )
    
    # Check if application is already accepted
    if application.status == "accepted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This application has already been accepted"
        )
    
    # Check if another applicant has already been selected for this gig
    all_applications = crud.get_gig_applications(db, application.gig_id)
    for app in all_applications:
        if app.status == "accepted" and app.id != application_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Another applicant has already been selected for this gig"
            )
    
    # Update application status to accepted
    updated_application = crud.update_application_status(db, application_id, "accepted")
    
    return updated_application


@router.put("/{application_id}/reject", response_model=schemas.ApplicationResponse)
def reject_applicant(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Reject an application.
    Only the gig owner can reject applications.
    """
    # Get the application
    application = crud.get_application(db, application_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Get the gig
    gig = crud.get_gig(db, application.gig_id)
    if not gig:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gig not found"
        )
    
    # Check if user is the gig owner
    if gig.owner_id != current_user["uid"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the gig owner can reject applications"
        )
    
    # Check if application is already rejected
    if application.status == "rejected":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This application has already been rejected"
        )
    
    # Update application status to rejected
    updated_application = crud.update_application_status(db, application_id, "rejected")
    
    return updated_application


@router.get("/{application_id}", response_model=schemas.ApplicationResponse)
def get_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get a specific application by ID.
    Only the gig owner or the applicant can view the application.
    """
    # Get the application
    application = crud.get_application(db, application_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Get the gig
    gig = crud.get_gig(db, application.gig_id)
    if not gig:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gig not found"
        )
    
    # Check if user is the gig owner or the applicant
    if gig.owner_id != current_user["uid"] and application.applicant_id != current_user["uid"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this application"
        )
    
    return application
