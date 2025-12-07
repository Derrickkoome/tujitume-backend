from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None


class UserCreate(UserBase):
    uid: str


class UserResponse(UserBase):
    uid: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Gig Schemas
class GigBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=20, max_length=5000)
    budget: Optional[float] = Field(None, gt=0)
    budget_type: Optional[str] = Field(None, pattern="^(fixed|hourly)$")
    location: Optional[str] = Field(None, max_length=200)
    skills_required: Optional[List[str]] = None
    deadline: Optional[datetime] = None


class GigCreate(GigBase):
    pass


class GigUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    description: Optional[str] = Field(None, min_length=20, max_length=5000)
    budget: Optional[float] = Field(None, gt=0)
    budget_type: Optional[str] = Field(None, pattern="^(fixed|hourly)$")
    location: Optional[str] = Field(None, max_length=200)
    skills_required: Optional[List[str]] = None
    deadline: Optional[datetime] = None


class GigResponse(GigBase):
    id: int
    owner_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Application Schemas
class ApplicationBase(BaseModel):
    cover_letter: str = Field(..., min_length=50)


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationResponse(ApplicationBase):
    id: int
    gig_id: int
    applicant_id: str
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Response models with relationships
class GigWithOwner(GigResponse):
    owner: Optional[UserResponse] = None


class ApplicationWithDetails(ApplicationResponse):
    gig: Optional[GigResponse] = None
    applicant: Optional[UserResponse] = None


# Review Schemas
class ReviewBase(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")
    comment: Optional[str] = None


class ReviewCreate(ReviewBase):
    gig_id: int
    reviewed_user_id: str  # UID of the user being reviewed


class ReviewResponse(ReviewBase):
    id: int
    gig_id: int
    reviewer_id: str
    reviewed_user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReviewWithDetails(ReviewResponse):
    reviewer: Optional[UserResponse] = None
    
    class Config:
        from_attributes = True


class UserReviewStats(BaseModel):
    average_rating: float
    total_reviews: int
    reviews: List[ReviewWithDetails] = []
