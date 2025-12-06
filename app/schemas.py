from pydantic import BaseModel
from typing import Optional, List

class ApplicationBase(BaseModel):
    pass

class ApplicationUpdate(BaseModel):
    status: str

class ApplicationResponse(BaseModel):
    id: int
    worker_id: int
    gig_id: int
    status: str

    class Config:
        from_attributes = True

# --- Gig Schemas ---
class GigBase(BaseModel):
    title: str
    description: str
    price: int

class GigResponse(GigBase):
    id: int
    client_id: int
    status: str
    applications: List[ApplicationResponse] = []

    class Config:
        from_attributes = True
        
        # --- Review Schemas ---
class ReviewBase(BaseModel):
    gig_id: int
    reviewee_id: int
    rating: int
    comment: str

class ReviewCreate(ReviewBase):
    pass

class ReviewResponse(ReviewBase):
    id: int
    reviewer_id: int

    class Config:
        from_attributes = True