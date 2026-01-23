print("✅ RUNNING FILE:", __file__)

import os
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

# Load backend/.env reliably (even if you run uvicorn from project root)
_HERE = os.path.dirname(os.path.abspath(__file__))            # .../backend/app
_ENV_PATH = os.path.abspath(os.path.join(_HERE, "..", ".env"))  # .../backend/.env
load_dotenv(dotenv_path=_ENV_PATH)
print("ENV FILE EXISTS:", os.path.exists(_ENV_PATH))


GOOGLE_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
if not GOOGLE_API_KEY:
    print(f"⚠️ GOOGLE_MAPS_API_KEY missing (expected in {_ENV_PATH})")
else:
    print(f"✅ GOOGLE_MAPS_API_KEY loaded (length={len(GOOGLE_API_KEY)}) from {_ENV_PATH}")

# ✅ CREATE APP FIRST
app = FastAPI(title="Deesha Backend", version="0.1.0")

# ✅ THEN middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ ROUTES ON app
@app.get("/health")
def health():
    return {"status": "ok"}


def _places_new_headers(field_mask: str | None = None) -> dict:
    headers = {
        "X-Goog-Api-Key": GOOGLE_API_KEY or "",
        "Content-Type": "application/json",
    }
    if field_mask:
        headers["X-Goog-FieldMask"] = field_mask
    return headers


def _places_new_post(url: str, body: dict, field_mask: str | None = None):
    """Call Places API (New) POST endpoints with consistent errors."""
    try:
        r = requests.post(url, json=body, headers=_places_new_headers(field_mask), timeout=12)
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Google request failed: {e}")

    # Places (New) uses normal HTTP status codes + JSON error payloads
    try:
        data = r.json()
    except ValueError:
        raise HTTPException(status_code=502, detail="Google returned non-JSON response")

    if r.status_code >= 400:
        raise HTTPException(status_code=502, detail=f"Google Places error: {data}")

    return data


def _places_new_get(url: str, field_mask: str | None = None):
    """Call Places API (New) GET endpoints with consistent errors."""
    try:
        r = requests.get(url, headers=_places_new_headers(field_mask), timeout=12)
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Google request failed: {e}")

    try:
        data = r.json()
    except ValueError:
        raise HTTPException(status_code=502, detail="Google returned non-JSON response")

    if r.status_code >= 400:
        raise HTTPException(status_code=502, detail=f"Google Places error: {data}")

    return data


@app.get("/places/autocomplete")
def places_autocomplete(input: str, sessiontoken: str | None = None, components: str | None = None):
    """Autocomplete suggestions for a text box.

    Example:
      /places/autocomplete?input=Dal&sessiontoken=abc123
    """
    if not GOOGLE_API_KEY:
        raise HTTPException(status_code=500, detail="Missing GOOGLE_MAPS_API_KEY")
    if not input:
        raise HTTPException(status_code=400, detail="Missing input")

    # Places API (New)
    url = "https://places.googleapis.com/v1/places:autocomplete"

    body: dict = {
        "input": input,
        # Strongly bias toward cities/regions
        "includedPrimaryTypes": ["locality", "administrative_area_level_1", "administrative_area_level_2"],
    }

    # Optional: restrict to US by default if you pass components=country:us
    # Places (New) uses regionCode instead of components.
    if components and "country:" in components:
        try:
            body["regionCode"] = components.split("country:", 1)[1].strip().upper()
        except Exception:
            pass

    if sessiontoken:
        body["sessionToken"] = sessiontoken

    # Places API (New) commonly requires a field mask for v1 endpoints
    field_mask = "suggestions.placePrediction.text,suggestions.placePrediction.placeId,suggestions.placePrediction.types"
    data = _places_new_post(url, body, field_mask=field_mask)

    suggestions = data.get("suggestions", [])

    preds = []
    for s in suggestions:
        pp = s.get("placePrediction") or {}
        text = (pp.get("text") or {}).get("text")
        place_id = pp.get("placeId")
        types = pp.get("types") or []
        if place_id:
            preds.append({"description": text, "place_id": place_id, "types": types})

    return {"predictions": preds}


@app.get("/places/details")
def place_details(place_id: str, sessiontoken: str | None = None):
    """Fetch details (name/address/lat/lng) for a place_id."""
    if not GOOGLE_API_KEY:
        raise HTTPException(status_code=500, detail="Missing GOOGLE_MAPS_API_KEY")
    if not place_id:
        raise HTTPException(status_code=400, detail="Missing place_id")

    # Places API (New)
    field_mask = "id,displayName,formattedAddress,location,types"
    url = f"https://places.googleapis.com/v1/places/{place_id}"

    # sessionToken is not supported on the GET place details endpoint; it's mainly for autocomplete.
    data = _places_new_get(url, field_mask=field_mask)

    loc = data.get("location") or {}
    display_name = (data.get("displayName") or {}).get("text")

    return {
        "place_id": data.get("id"),
        "name": display_name,
        "formatted_address": data.get("formattedAddress"),
        "lat": loc.get("latitude"),
        "lng": loc.get("longitude"),
        "types": data.get("types", []),
    }

class ResolvePlaceRequest(BaseModel):
    text: str
    sessiontoken: str | None = None


class LatLng(BaseModel):
    lat: float
    lng: float
    place_id: Optional[str] = None


class RoutesRequest(BaseModel):
    start: LatLng
    destination: LatLng
    # Optional intermediate stops (e.g., B). Frontend may send: {"waypoints": [{"lat":..,"lng":..}]}
    waypoints: List[LatLng] = []


class AlternativesRequest(BaseModel):
    start: LatLng
    destination: LatLng
    interests: List[str] = []

@app.post("/places/resolve")
def resolve_place(payload: ResolvePlaceRequest = Body(...)):
    """Resolve a free-text place string into a canonical place_id + lat/lng.

    Frontend can POST: {"text": "Dallas, TX", "sessiontoken": "abc123"}
    """
    if not GOOGLE_API_KEY:
        raise HTTPException(status_code=500, detail="Missing GOOGLE_MAPS_API_KEY")

    text = payload.text
    sessiontoken = payload.sessiontoken

    # 1) Search Text (Places API (New))
    url = "https://places.googleapis.com/v1/places:searchText"
    field_mask = "places.id,places.displayName,places.formattedAddress,places.location,places.types"

    body: dict = {"textQuery": text}
    if sessiontoken:
        body["sessionToken"] = sessiontoken

    data = _places_new_post(url, body, field_mask=field_mask)
    places = data.get("places", [])
    if not places:
        return {"status": "ZERO_RESULTS", "query": text, "place": None}

    top = places[0] or {}
    place_id = top.get("id")

    # 2) Normalize response to our app shape
    loc = top.get("location") or {}
    name = (top.get("displayName") or {}).get("text")

    return {
        "status": "OK",
        "query": text,
        "place": {
            "place_id": place_id,
            "name": name,
            "formatted_address": top.get("formattedAddress"),
            "lat": loc.get("latitude"),
            "lng": loc.get("longitude"),
            "types": top.get("types", []),
        },
    }


def _format_distance_meters(m: int | None) -> str | None:
    if m is None:
        return None
    miles = m / 1609.344
    if miles < 10:
        return f"{miles:.1f} mi"
    return f"{round(miles)} mi"


def _format_duration_seconds(seconds: int | None) -> str | None:
    if seconds is None:
        return None
    minutes = int(round(seconds / 60))
    if minutes < 60:
        return f"{minutes} min"
    h = minutes // 60
    m = minutes % 60
    return f"{h} hr {m} min" if m else f"{h} hr"


def _parse_duration_to_seconds(dur: str | None) -> int | None:
    # Routes API returns durations like "1234s"
    if not dur or not isinstance(dur, str):
        return None
    if dur.endswith("s"):
        try:
            return int(float(dur[:-1]))
        except Exception:
            return None
    return None



@app.post("/routes")
def routes(req: RoutesRequest):
    """Return a driving route polyline + distance/duration.

    Expects:
      {"start":{"lat":..,"lng":..},"destination":{"lat":..,"lng":..},"waypoints":[{"lat":..,"lng":..}]}

    Returns:
      {"polyline":"...","distance_text":"...","duration_text":"..."}
    """
    if not GOOGLE_API_KEY:
        raise HTTPException(status_code=500, detail="Missing GOOGLE_MAPS_API_KEY")

    url = "https://routes.googleapis.com/directions/v2:computeRoutes"

    body = {
        "origin": {"location": {"latLng": {"latitude": req.start.lat, "longitude": req.start.lng}}},
        "destination": {"location": {"latLng": {"latitude": req.destination.lat, "longitude": req.destination.lng}}},
        "travelMode": "DRIVE",
        "routingPreference": "TRAFFIC_AWARE",
        "computeAlternativeRoutes": False,
    }
    # If we have intermediate waypoints, route A -> waypoint(s) -> C
    body["intermediates"] = [
    {
        "location": {
            "latLng": {
                "latitude": w.lat,
                "longitude": w.lng
            }
        },
        "via": True   # 🔥 THIS IS THE KEY
    }
    for w in req.waypoints
]

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_API_KEY,
        "X-Goog-FieldMask": "routes.distanceMeters,routes.duration,routes.polyline.encodedPolyline",
    }

    try:
        r = requests.post(url, json=body, headers=headers, timeout=20)
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Google request failed: {e}")

    try:
        data = r.json()
    except ValueError:
        raise HTTPException(status_code=502, detail="Google returned non-JSON response")

    if r.status_code >= 400:
        raise HTTPException(status_code=502, detail=f"Google Routes error: {data}")

    routes_list = data.get("routes") or []
    if not routes_list:
        raise HTTPException(status_code=404, detail="No routes returned")

    rt = routes_list[0]
    dist_m = rt.get("distanceMeters")
    dur_s = _parse_duration_to_seconds(rt.get("duration"))
    poly = (rt.get("polyline") or {}).get("encodedPolyline")

    return {
        "polyline": poly,
        "distance_meters": dist_m,
        "duration_seconds": dur_s,
        "distance_text": _format_distance_meters(dist_m),
        "duration_text": _format_duration_seconds(dur_s),
    }


@app.post("/places/alternatives")
def places_alternatives(req: AlternativesRequest):
    """Return one suggested stop near the midpoint between start and destination.

    This is an MVP endpoint used by the frontend Replace button.
    """
    if not GOOGLE_API_KEY:
        raise HTTPException(status_code=500, detail="Missing GOOGLE_MAPS_API_KEY")

    mid_lat = (req.start.lat + req.destination.lat) / 2.0
    mid_lng = (req.start.lng + req.destination.lng) / 2.0

    interest_map = {
        "food": ["restaurant", "cafe"],
        "scenic": ["tourist_attraction", "park"],
        "nature": ["park"],
        "hiking": ["park"],
        "photo": ["tourist_attraction"],
        "nightlife": ["bar", "night_club"],
        "relax": ["spa"],
        "adventure": ["amusement_park"],
        "hidden": ["tourist_attraction"],
    }

    included: List[str] = []
    for k in (req.interests or []):
        included += interest_map.get(k, [])

    # default if user picked nothing
    if not included:
        included = ["tourist_attraction"]

    # dedupe & keep small (keeps Google cost lower)
    included = list(dict.fromkeys(included))[:3]

    url = "https://places.googleapis.com/v1/places:searchNearby"
    field_mask = "places.id,places.displayName,places.formattedAddress,places.location,places.types"

    body = {
        "includedTypes": included,
        "maxResultCount": 5,
        "locationRestriction": {
            "circle": {
                "center": {"latitude": mid_lat, "longitude": mid_lng},
                "radius": 30000.0,
            }
        },
    }

    data = _places_new_post(url, body, field_mask=field_mask)
    places = data.get("places") or []
    if not places:
        raise HTTPException(status_code=404, detail="No alternatives found")

    p = places[0] or {}
    name = (p.get("displayName") or {}).get("text") or "New stop"
    loc = p.get("location") or {}

    return {
        "title": name,
        "place_id": p.get("id"),
        "formatted_address": p.get("formattedAddress"),
        "lat": loc.get("latitude"),
        "lng": loc.get("longitude"),
        "types": p.get("types", []),
        "stay": "1 hr",
    }

# ✅ Include additional API routers (kept separate in backend/app/routes/*.py)
from .routes.trip import router as trip_router
app.include_router(trip_router)
