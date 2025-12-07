from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.dependencies import get_db, get_current_user
from app.crud import crud
from app.schemas import schemas

router = APIRouter(
    prefix="/api",
    tags=["reviews"]
)


@router.post("/gigs/{gig_id}/complete", response_model=schemas.GigResponse)
def complete_gig(
    gig_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Mark a gig as completed.
    Only the gig owner can mark it as completed.
    Gig must have an accepted application.
    """
    # Get the gig
    gig = crud.get_gig(db, gig_id)
    if not gig:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gig not found"
        )
    
    # Check if user is the gig owner
    if gig.owner_id != current_user["uid"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the gig owner can mark it as completed"
        )
    
    # Check if gig is already completed
    if gig.is_completed == "true":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Gig is already marked as completed"
        )
    
    # Check if there's an accepted application
    applications = crud.get_gig_applications(db, gig_id)
    has_accepted = any(app.status == "accepted" for app in applications)
    
    if not has_accepted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Gig must have an accepted application before marking as completed"
        )
    
    # Mark gig as completed
    updated_gig = crud.mark_gig_completed(db, gig_id)
    
    return updated_gig


@router.post("/reviews", response_model=schemas.ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    review: schemas.ReviewCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a review for a user after completing a gig.
    Client can review worker, worker can review client.
    """
    # Get the gig
    gig = crud.get_gig(db, review.gig_id)
    if not gig:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gig not found"
        )
    
    # Check if gig is completed
    if gig.is_completed != "true":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only review after gig is completed"
        )
    
    # Check if user is involved in the gig (either owner or accepted worker)
    applications = crud.get_gig_applications(db, review.gig_id)
    accepted_app = next((app for app in applications if app.status == "accepted"), None)
    
    is_owner = gig.owner_id == current_user["uid"]
    is_worker = accepted_app and accepted_app.applicant_id == current_user["uid"]
    
    if not (is_owner or is_worker):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be involved in the gig to leave a review"
        )
    
    # Validate that reviewed_user_id is the other party
    if is_owner and review.reviewed_user_id != accepted_app.applicant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="As gig owner, you can only review the accepted worker"
        )
    
    if is_worker and review.reviewed_user_id != gig.owner_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="As worker, you can only review the gig owner"
        )
    
    # Check if user already reviewed this person for this gig
    existing_review = crud.check_existing_review(
        db, 
        review.gig_id, 
        current_user["uid"], 
        review.reviewed_user_id
    )
    
    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already reviewed this user for this gig"
        )
    
    # Create review
    review_data = {
        "gig_id": review.gig_id,
        "reviewer_id": current_user["uid"],
        "reviewed_user_id": review.reviewed_user_id,
        "rating": review.rating,
        "comment": review.comment
    }
    
    new_review = crud.create_review(db, review_data)
    
    return new_review


@router.get("/reviews/{user_id}", response_model=schemas.UserReviewStats)
def get_user_reviews(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Get all reviews and stats for a specific user.
    Returns average rating, total reviews, and list of reviews.
    """
    # Check if user exists
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get all reviews for this user
    reviews = crud.get_user_reviews(db, user_id)
    
    # Calculate stats
    total_reviews = len(reviews)
    average_rating = sum(r.rating for r in reviews) / total_reviews if total_reviews > 0 else 0.0
    
    return {
        "average_rating": round(average_rating, 2),
        "total_reviews": total_reviews,
        "reviews": reviews
    }
