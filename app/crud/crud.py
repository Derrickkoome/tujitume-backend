from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional
from app.models.models import User, Gig, Application, Review
from app.schemas import schemas
from datetime import datetime


# User CRUD
def get_user(db: Session, uid: str) -> Optional[User]:
    return db.query(User).filter(User.uid == uid).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate) -> User:
    db_user = User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_or_create_user(db: Session, uid: str, email: str, name: Optional[str] = None) -> User:
    user = get_user(db, uid)
    if not user:
        user_data = schemas.UserCreate(uid=uid, email=email, name=name)
        user = create_user(db, user_data)
    return user


# Gig CRUD
def get_gig(db: Session, gig_id: int) -> Optional[Gig]:
    return db.query(Gig).filter(Gig.id == gig_id).first()


def get_gigs(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    budget_type: Optional[str] = None,
    skills: Optional[List[str]] = None,
    search: Optional[str] = None
) -> List[Gig]:
    query = db.query(Gig)
    
    # Filter by budget type
    if budget_type and budget_type in ["fixed", "hourly"]:
        query = query.filter(Gig.budget_type == budget_type)
    
    # Filter by skills
    if skills and len(skills) > 0:
        # Check if any of the requested skills are in the gig's skills_required
        query = query.filter(
            or_(*[Gig.skills_required.contains([skill]) for skill in skills])
        )
    
    # Search in title, description, or location
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Gig.title.ilike(search_pattern),
                Gig.description.ilike(search_pattern),
                Gig.location.ilike(search_pattern)
            )
        )
    
    # Sorting
    if sort_by == "budget" and sort_order == "desc":
        query = query.order_by(Gig.budget.desc())
    elif sort_by == "budget" and sort_order == "asc":
        query = query.order_by(Gig.budget.asc())
    elif sort_by == "created_at" and sort_order == "asc":
        query = query.order_by(Gig.created_at.asc())
    else:  # default: created_at desc
        query = query.order_by(Gig.created_at.desc())
    
    return query.offset(skip).limit(limit).all()


def get_user_gigs(db: Session, owner_id: str) -> List[Gig]:
    return db.query(Gig).filter(Gig.owner_id == owner_id).order_by(Gig.created_at.desc()).all()


def create_gig(db: Session, gig: schemas.GigCreate, owner_id: str) -> Gig:
    db_gig = Gig(**gig.model_dump(), owner_id=owner_id)
    db.add(db_gig)
    db.commit()
    db.refresh(db_gig)
    return db_gig


def update_gig(db: Session, gig_id: int, gig_update: schemas.GigUpdate) -> Optional[Gig]:
    db_gig = get_gig(db, gig_id)
    if not db_gig:
        return None
    
    update_data = gig_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_gig, key, value)
    
    db_gig.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_gig)
    return db_gig


def delete_gig(db: Session, gig_id: int) -> bool:
    db_gig = get_gig(db, gig_id)
    if not db_gig:
        return False
    db.delete(db_gig)
    db.commit()
    return True


# Application CRUD
def get_application(db: Session, application_id: int) -> Optional[Application]:
    return db.query(Application).filter(Application.id == application_id).first()


def get_gig_applications(db: Session, gig_id: int) -> List[Application]:
    return db.query(Application).filter(Application.gig_id == gig_id).order_by(Application.created_at.desc()).all()


def get_user_applications(db: Session, applicant_id: str) -> List[Application]:
    return db.query(Application).filter(Application.applicant_id == applicant_id).order_by(Application.created_at.desc()).all()


def check_existing_application(db: Session, gig_id: int, applicant_id: str) -> Optional[Application]:
    return db.query(Application).filter(
        and_(Application.gig_id == gig_id, Application.applicant_id == applicant_id)
    ).first()


def create_application(db: Session, application: schemas.ApplicationCreate, gig_id: int, applicant_id: str) -> Application:
    db_application = Application(
        **application.model_dump(),
        gig_id=gig_id,
        applicant_id=applicant_id
    )
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application


def update_application_status(db: Session, application_id: int, status: str) -> Optional[Application]:
    db_application = get_application(db, application_id)
    if not db_application:
        return None
    
    db_application.status = status
    db_application.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_application)
    return db_application


# ========== REVIEWS ==========

def create_review(db: Session, review_data: dict) -> Review:
    """Create a new review"""
    review = Review(**review_data)
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def get_user_reviews(db: Session, user_id: str) -> List[Review]:
    """Get all reviews for a specific user"""
    return db.query(Review)\
        .filter(Review.reviewed_user_id == user_id)\
        .order_by(Review.created_at.desc())\
        .all()


def get_review(db: Session, review_id: int) -> Optional[Review]:
    """Get a review by ID"""
    return db.query(Review).filter(Review.id == review_id).first()


def check_existing_review(db: Session, gig_id: int, reviewer_id: str, reviewed_user_id: str) -> Optional[Review]:
    """Check if a review already exists for this gig from this reviewer to this user"""
    return db.query(Review)\
        .filter(
            Review.gig_id == gig_id,
            Review.reviewer_id == reviewer_id,
            Review.reviewed_user_id == reviewed_user_id
        )\
        .first()


# ========== GIG COMPLETION ==========

def mark_gig_completed(db: Session, gig_id: int) -> Optional[Gig]:
    """Mark a gig as completed"""
    gig = db.query(Gig).filter(Gig.id == gig_id).first()
    if gig:
        gig.is_completed = "true"
        db.commit()
        db.refresh(gig)
    return gig
