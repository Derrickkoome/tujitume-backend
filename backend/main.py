from fastapi import FastAPI
from routers.auth_routes import router as auth_router
from routers.gig_routes import router as gig_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(gig_router)

@app.get("/")
def home():
    return {"message": "Backend running!"}
