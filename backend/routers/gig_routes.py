from fastapi import APIRouter, Depends
from auth.dependencies import verify_firebase_token 

router = APIRouter(prefix="/gigs", tags=["Gigs"])

# temporary mock data
GIGS = [
    {
        "id": 1,
        "title": "Laundry Service",
        "description": "Wash and fold clothes quickly.",
        "category": "Cleaning",
        "location": "Eastleigh",
        "price": 300,
    },
    {
        "id": 2,
        "title": "Dishwashing",
        "description": "Help wash utensils for a small family.",
        "category": "Kitchen",
        "location": "South B",
        "price": 150,
    },
]

@router.get("")
async def get_gigs(user=Depends(verify_firebase_token)):
    return GIGS

@router.get("/{gig_id}")
async def get_gig(gig_id: int, user=Depends(verify_firebase_token)):
    for gig in GIGS:
        if gig["id"] == gig_id:
            return gig
    return {"error": "Gig not found"}
