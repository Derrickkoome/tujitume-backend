from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Float, Text
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    role = Column(String)  # 'client' or 'worker'

class Gig(Base):
    __tablename__ = "gigs"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    price = Column(Integer)
    status = Column(String, default="OPEN")  # OPEN, IN_PROGRESS, COMPLETED
    client_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    client = relationship("User", backref="posted_gigs")
    applications = relationship("Application", back_populates="gig")

class Application(Base):
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey("users.id"))
    gig_id = Column(Integer, ForeignKey("gigs.id"))
    status = Column(String, default="PENDING")  # PENDING, ACCEPTED, REJECTED
    
    # Relationships
    gig = relationship("Gig", back_populates="applications")
    worker = relationship("User")

class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    gig_id = Column(Integer, ForeignKey("gigs.id"))
    reviewer_id = Column(Integer, ForeignKey("users.id"))
    reviewee_id = Column(Integer, ForeignKey("users.id"))
    rating = Column(Integer)
    comment = Column(Text)