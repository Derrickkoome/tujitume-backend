from fastapi import FastAPI
from .database import engine, Base
from .routers import applications, gigs, reviews

# 1. Create the Database Tables
Base.metadata.create_all(bind=engine)

# 2. Initialize the App (This creates the 'app' variable)
app = FastAPI(title="Tujitume Backend")

# 3. Define the Root Endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to Tujitume API"}

# 4. Connect the Routers (Now 'app' exists, so this works!)
app.include_router(applications.router)
app.include_router(gigs.router)
app.include_router(reviews.router)