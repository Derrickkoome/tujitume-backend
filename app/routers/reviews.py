from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, database

router = APIRouter(prefix="/reviews", tags=["Reviews"])

# 1. POST A REVIEW
@router.post("/", response_model=schemas.ReviewResponse)
def create_review(
    review: schemas.ReviewCreate, 
    db: Session = Depends(database.get_db),
    current_user_id: int = 1 # Simulating logged-in user
):
    # Verify the Gig exists and is COMPLETED
    gig = db.query(models.Gig).filter(models.Gig.id == review.gig_id).first()
    if not gig or gig.status != "COMPLETED":
        raise HTTPException(status_code=400, detail="Cannot review a gig that is not completed")

    new_review = models.Review(
        gig_id=review.gig_id,
        reviewer_id=current_user_id,
        reviewee_id=review.reviewee_id,
        rating=review.rating,
        comment=review.comment
    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review

# 2. SEE REVIEWS (Reputation)
@router.get("/{user_id}", response_model=List[schemas.ReviewResponse])
def get_user_reviews(user_id: int, db: Session = Depends(database.get_db)):
    reviews = db.query(models.Review).filter(models.Review.reviewee_id == user_id).all()
    return reviews