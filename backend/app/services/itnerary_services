from __future__ import annotations

from typing import List

from app.models.schemas import TripRequest, TripResponse, DayPlan, Stop
from app.utils.logic import normalize_text, pick_mid_stop


def build_itinerary(req: TripRequest) -> TripResponse:
    start_city = normalize_text(req.start_city)
    destination = normalize_text(req.destination)
    state = normalize_text(req.destination_state or "")

    days = req.days if req.days and req.days > 0 else 3
    interests: List[str] = req.interests or []

    mid_stop = pick_mid_stop(interests)

    plans: List[DayPlan] = []
    for d in range(1, days + 1):
        stops = [
            Stop(title="Start easy + coffee", category="warmup"),
            Stop(mid_stop, category="highlight"),
            Stop("Dinner + chill", category="food"),
        ]
        plans.append(DayPlan(day=d, title=f"Day {d} in {destination or 'your trip'}", stops=stops))

    summary = f"{start_city or 'Start'} → {destination or 'Destination'} ({state or 'State'}) • {days} days"

    return TripResponse(
        summary=summary,
        start_city=start_city,
        destination=destination,
        destination_state=state,
        days=plans,
    )
