print("✅ LOADED FILE:", __file__)

import os
import requests
from fastapi import APIRouter, HTTPException

# This file must define a ROUTER, not a new FastAPI() app.
# Your main app (e.g., backend/app/main.py) should do: app.include_router(router)

router = APIRouter(tags=["trip"])


@router.post("/legacy/places/resolve")
def places_resolve_legacy(payload: dict):
    """LEGACY endpoint (kept only for reference).

    NOTE: You already have a modern `/places/resolve` in your main app that uses Places API (New).
    This legacy route is renamed to `/legacy/places/resolve` to avoid route conflicts.

    Expects: {"text": "Dallas, TX"}
    Returns: {"place_id":..., "name":..., "lat":..., "lng":...}
    """

    google_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not google_api_key:
        raise HTTPException(
            status_code=500,
            detail="Missing GOOGLE_MAPS_API_KEY in backend environment",
        )

    text = (payload or {}).get("text")
    if not text:
        raise HTTPException(status_code=400, detail="Missing text")

    # 1) Autocomplete (legacy)
    auto_url = "https://maps.googleapis.com/maps/api/place/autocomplete/json"
    try:
        auto_res = requests.get(
            auto_url,
            params={"input": text, "key": google_api_key},
            timeout=15,
        ).json()
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Google request failed: {e}")

    predictions = auto_res.get("predictions") or []
    if not predictions:
        raise HTTPException(status_code=404, detail="No place found")

    place_id = predictions[0].get("place_id")
    if not place_id:
        raise HTTPException(status_code=500, detail="No place_id returned by Google")

    # 2) Place Details (legacy)
    details_url = "https://maps.googleapis.com/maps/api/place/details/json"
    try:
        details_res = requests.get(
            details_url,
            params={"place_id": place_id, "fields": "name,geometry", "key": google_api_key},
            timeout=15,
        ).json()
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Google request failed: {e}")

    result = details_res.get("result") or {}
    location = (result.get("geometry") or {}).get("location") or {}

    lat = location.get("lat")
    lng = location.get("lng")
    if lat is None or lng is None:
        raise HTTPException(status_code=500, detail="No lat/lng returned by Google")

    return {"place_id": place_id, "name": result.get("name") or text, "lat": lat, "lng": lng}
