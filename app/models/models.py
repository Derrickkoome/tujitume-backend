from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class User(Base):
    __tablename__ = "users"
    
    uid = Column(String, primary_key=True, index=True)  # Firebase UID
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String)
    bio = Column(Text)  # User bio/description
    skills = Column(JSON)  # Array of skills
    phone = Column(String)  # Contact phone number
    location = Column(String)  # User location
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    gigs = relationship("Gig", back_populates="owner", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="applicant", cascade="all, delete-orphan")


class Gig(Base):
    __tablename__ = "gigs"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=False)
    budget = Column(Float)
    budget_type = Column(String)  # "fixed" or "hourly"
    location = Column(String)
    skills_required = Column(JSON)  # Array of strings
    deadline = Column(DateTime)
    owner_id = Column(String, ForeignKey("users.uid"), nullable=False)
    is_completed = Column(String, default="false")  # "false", "true"
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="gigs")
    applications = relationship("Application", back_populates="gig", cascade="all, delete-orphan")


class Application(Base):
    __tablename__ = "applications"
    
    id = Column(Integer, primary_key=True, index=True)
    gig_id = Column(Integer, ForeignKey("gigs.id"), nullable=False)
    applicant_id = Column(String, ForeignKey("users.uid"), nullable=False)
    cover_letter = Column(Text)
    status = Column(String, default="pending")  # pending, accepted, rejected
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    gig = relationship("Gig", back_populates="applications")
    applicant = relationship("User", back_populates="applications")


class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    gig_id = Column(Integer, ForeignKey("gigs.id"), nullable=False)
    reviewer_id = Column(String, ForeignKey("users.uid"), nullable=False)  # Who wrote the review
    reviewed_user_id = Column(String, ForeignKey("users.uid"), nullable=False)  # Who is being reviewed
    rating = Column(Integer, nullable=False)  # 1-5 stars
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    reviewer = relationship("User", foreign_keys=[reviewer_id])
    reviewed_user = relationship("User", foreign_keys=[reviewed_user_id])
