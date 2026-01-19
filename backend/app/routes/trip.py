from fastapi import APIRouter

from app.models.schemas import TripRequest, TripResponse
from app.services.itinerary_service import build_itinerary

router = APIRouter()

@router.post("/plan-trip", response_model=TripResponse)
def plan_trip(req: TripRequest) -> TripResponse:
    return build_itinerary(req)
