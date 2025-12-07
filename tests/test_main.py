from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app import models
import pytest

# 1. SETUP TEST DATABASE (In-Memory SQLite)
# We use 'connect_args={"check_same_thread": False}' for SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool # Important for in-memory tests
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the database dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# 2. SETUP DATA BEFORE TESTS
@pytest.fixture(scope="module", autouse=True)
def setup_database():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Add Dummy Data
    db = TestingSessionLocal()
    
    # Create Client (ID 1) and Worker (ID 2)
    client_user = models.User(name="Test Client", email="client@test.com", role="client")
    worker_user = models.User(name="Test Worker", email="worker@test.com", role="worker")
    db.add(client_user)
    db.add(worker_user)
    db.commit()
    
    # Create a Gig (ID 1)
    gig = models.Gig(
        title="Test Gig", 
        description="Test Desc", 
        price=1000, 
        status="OPEN", 
        client_id=1
    )
    db.add(gig)
    db.commit()
    
    # Create an Application (ID 1)
    application = models.Application(worker_id=2, gig_id=1, status="PENDING")
    db.add(application)
    db.commit()
    db.close()
    
    yield
    
    # Clean up after tests
    Base.metadata.drop_all(bind=engine)

# 3. ACTUAL TESTS

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Tujitume API"}

def test_select_worker():
    # Try to select the worker for the gig (ID 1)
    response = client.put("/applications/1/select")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ACCEPTED"

def test_complete_gig():
    # Try to mark gig as complete
    # Note: It relies on the previous test setting status to IN_PROGRESS
    response = client.put("/gigs/1/complete")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "COMPLETED"

def test_create_review():
    # Post a review for the completed gig
    payload = {
        "gig_id": 1,
        "reviewee_id": 2,
        "rating": 5,
        "comment": "Excellent work!"
    }
    response = client.post("/reviews/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["comment"] == "Excellent work!"
    assert data["rating"] == 5