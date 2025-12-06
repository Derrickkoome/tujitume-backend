from fastapi import FastAPI
from .database import engine, Base
from .routers import applications, gigs

# This command creates the database tables automatically
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Tujitume Backend")

@app.get("/")
def read_root():
    return {"message": "Welcome to Tujitume API"}

# Register the routers
app.include_router(applications.router)
# app.include_router(gigs.router) # We will enable this in the next task