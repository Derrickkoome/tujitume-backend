from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models, schemas, database

router = APIRouter(prefix="/applications", tags=["Applications"])

@router.put("/{application_id}/select", response_model=schemas.ApplicationResponse)
def select_worker(
    application_id: int,
    db: Session = Depends(database.get_db),
    # NOTE: Since Authentication (Task 8) isn't finished yet, 
    # we will simulate that User #1 is logged in. 
    # Later, you will replace this with: current_user = Depends(get_current_user)
    current_user_id: int = 1 
):
    # 1. GET THE APPLICATION
    application = db.query(models.Application).filter(models.Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    # 2. GET THE GIG ASSOCIATED WITH THIS APPLICATION
    gig = application.gig

    # 3. VALIDATION: ONLY THE CLIENT WHO POSTED THE GIG CAN SELECT A WORKER
    if gig.client_id != current_user_id:
        raise HTTPException(
            status_code=403, 
            detail="Not authorized to select workers for this gig"
        )

    # 4. VALIDATION: CHECK IF GIG IS ALREADY FILLED
    if gig.status != "OPEN":
        raise HTTPException(
            status_code=400, 
            detail="This gig is no longer open for selection"
        )

    # 5. EXECUTE THE LOGIC
    # Update application status to ACCEPTED
    application.status = "ACCEPTED"
    
    # Update gig status to IN_PROGRESS (so no one else can apply)
    gig.status = "IN_PROGRESS"
    
    # Save changes
    db.commit()
    db.refresh(application)
    
    return application