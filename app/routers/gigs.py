from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, database

# This line creates the 'router' variable that was missing
router = APIRouter(prefix="/gigs", tags=["Gigs"])

# 1. COMPLETION ENDPOINT (Task 13)
@router.put("/{gig_id}/complete", response_model=schemas.GigResponse)
def complete_gig(
    gig_id: int, 
    db: Session = Depends(database.get_db),
    current_user_id: int = 1 # Simulating logged-in Client (Mama Mboga)
):
    # Get the gig
    gig = db.query(models.Gig).filter(models.Gig.id == gig_id).first()
    if not gig:
        raise HTTPException(status_code=404, detail="Gig not found")

    # Check authorization (Only the owner can complete it)
    if gig.client_id != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to complete this gig")

    # Check status (Can only complete if it was In Progress)
    if gig.status != "IN_PRO   GRESS":
        raise HTTPException(status_code=400, detail="Gig must be IN_PROGRESS to mark as complete")

    gig.status = "COMPLETED"
    db.commit()
    db.refresh(gig)
    return gig