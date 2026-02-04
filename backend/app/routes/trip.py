print("✅ LOADED FILE:", __file__)

# NOTE:
# This module now only holds **legacy** endpoints under the `/legacy` prefix.
# The real, production endpoints for:
#   - POST /places/resolve
#   - POST /places/things-to-do
# live in `app/main.py` and use the newer Places API flow.
# You generally do NOT need to modify this file for the normal app behaviour.

import os
import math
from typing import Dict, Any

import requests
from fastapi import APIRouter, HTTPException

# 🔒 Legacy-only router (everything here is under /legacy)
router = APIRouter(prefix="/legacy", tags=["trip-legacy"])

# -------------------------------------------------------------------
# 1) LEGACY Google Places resolver (OLD API) - /legacy/places/resolve
# -------------------------------------------------------------------

@router.post("/places/resolve")
def legacy_places_resolve(payload: Dict[str, Any]):
    """
    LEGACY Google Places (OLD API) resolver.

    Path:
      POST /legacy/places/resolve

    Body:
      { "text": "Dallas, TX" }

    NOTE:
    - main.py already defines the REAL `/places/resolve`
      using Places API (New).
    - This endpoint is kept only for fallback/testing.
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

    # 1️⃣ Autocomplete (OLD API)
    try:
        auto_res = requests.get(
            "https://maps.googleapis.com/maps/api/place/autocomplete/json",
            params={
                "input": text,
                "key": google_api_key,
            },
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

    # 2️⃣ Place Details (OLD API)
    try:
        details_res = requests.get(
            "https://maps.googleapis.com/maps/api/place/details/json",
            params={
                "place_id": place_id,
                "fields": "name,geometry",
                "key": google_api_key,
            },
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

    return {
        "place_id": place_id,
        "name": result.get("name") or text,
        "lat": lat,
        "lng": lng,
    }


# -------------------------------------------------------------------
# 2) LEGACY "Things to do" (OLD API) - /legacy/places/things-to-do
# -------------------------------------------------------------------

EARTH_RADIUS_M = 6371000
MILES_20_M = 32187
MILES_30_M = 48280


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Distance in meters between two lat/lng points.
    """
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * EARTH_RADIUS_M * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def midpoint(a: Dict[str, float], b: Dict[str, float]) -> Dict[str, float]:
    """
    Simple midpoint between two (lat,lng) dicts.
    """
    return {"lat": (a["lat"] + b["lat"]) / 2.0, "lng": (a["lng"] + b["lng"]) / 2.0}


@router.post("/places/things-to-do")
def legacy_things_to_do(payload: Dict[str, Any]):
    """
    LEGACY version of "Things to do" using the OLD Places Text Search API.

    Path:
      POST /legacy/places/things-to-do

    Body example:
    {
      "start": {"lat": 32.7767, "lng": -96.7970},
      "destination": {"lat": 30.2672, "lng": -97.7431},
      "mood": "scenic",
      "limit": 12
    }

    NOTE:
    - main.py already defines the new `/places/things-to-do`
      that uses the New Places API (v1).
    - This endpoint is kept for debugging/fallback.
    """

    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Missing GOOGLE_MAPS_API_KEY")

    start = payload.get("start")
    destination = payload.get("destination")
    mood = (payload.get("mood") or "scenic").lower()
    limit = int(payload.get("limit", 12))

    if not start or not destination:
        raise HTTPException(status_code=400, detail="Missing start/destination")

    # Mood → text queries
    MOOD_QUERIES = {
        "hiking": ["parks", "hiking trails", "nature reserve"],
        "scenic": ["tourist attractions", "scenic viewpoints"],
        "food": ["restaurants", "cafes"],
        "photo": ["tourist attractions", "viewpoints"],
        "culture": ["museums", "historical places"],
        "adventure": ["amusement park", "outdoor activities"],
        "relax": ["parks", "botanical garden", "spa"],
    }

    queries = MOOD_QUERIES.get(mood, ["tourist attractions"])

    results: Dict[str, Dict[str, Any]] = {}

    def text_search(lat: float, lng: float, radius_m: float):
        for q in queries:
            try:
                res = requests.post(
                    "https://places.googleapis.com/v1/places:searchText",
                    headers={
                        "Content-Type": "application/json",
                        "X-Goog-Api-Key": api_key,
                        "X-Goog-FieldMask": (
                            "places.id,places.displayName,places.location,"
                            "places.rating,places.userRatingCount,places.types"
                        ),
                    },
                    json={
                        "textQuery": f"{q} near this location",
                        "locationBias": {
                            "circle": {
                                "center": {"latitude": lat, "longitude": lng},
                                "radius": float(radius_m),
                            }
                        },
                        "maxResultCount": 20,
                    },
                    timeout=20,
                ).json()
            except requests.RequestException as e:
                raise HTTPException(status_code=502, detail=f"Google request failed: {e}")

            for p in res.get("places", []):
                pid = p.get("id")
                if pid:
                    results[pid] = p

    # 1) Along route (midpoint)
    mid = midpoint(start, destination)
    text_search(mid["lat"], mid["lng"], MILES_20_M)

    # 2) Near destination
    text_search(destination["lat"], destination["lng"], MILES_30_M)

    # Rank by popularity
    def popularity_score(p: Dict[str, Any]) -> float:
        rating = float(p.get("rating") or 0.0)
        votes = float(p.get("userRatingCount") or 0.0)
        return rating * math.log(votes + 1.0)

    ranked = sorted(results.values(), key=popularity_score, reverse=True)

    out = []
    for p in ranked[:limit]:
        loc = p.get("location") or {}
        out.append(
            {
                "place_id": p.get("id"),
                "title": (p.get("displayName") or {}).get("text"),
                "lat": loc.get("latitude"),
                "lng": loc.get("longitude"),
                "rating": p.get("rating"),
                "votes": p.get("userRatingCount"),
                "types": p.get("types", []),
            }
        )

    return {"results": out, "mood": mood, "count": len(out)}
