print("✅ RUNNING FILE:", __file__)

import os
import math
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

# -------------------------------------------------
# Load environment (.env) from backend/.env
# -------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))          # .../backend/app
_ENV_PATH = os.path.abspath(os.path.join(_HERE, "..", ".env"))  # .../backend/.env
load_dotenv(dotenv_path=_ENV_PATH)
print("ENV FILE EXISTS:", os.path.exists(_ENV_PATH))

GOOGLE_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
# SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")  # optional: for internet search + grounding (disabled for now)
SERPAPI_API_KEY = None
if not GOOGLE_API_KEY:
    print(f"⚠️ GOOGLE_MAPS_API_KEY missing (expected in {_ENV_PATH})")
else:
    print(f"✅ GOOGLE_MAPS_API_KEY loaded (length={len(GOOGLE_API_KEY)}) from {_ENV_PATH}")

# -------------------------------------------------
# FastAPI app + CORS
# -------------------------------------------------
app = FastAPI(title="Deesha Backend", version="0.1.0")

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


@app.get("/health")
def health():
    return {"status": "ok"}


# -------------------------------------------------
# Helpers for Places API (New)
# -------------------------------------------------
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


# -------------------------------------------------
# Optional: Web Search (SerpAPI) + "grounding" via Places
# NOTE: SerpAPI is intentionally disabled for now (budget). Code can be added later.
# -------------------------------------------------


# -------------------------------------------------
# /places/autocomplete (GET + POST)
# -------------------------------------------------
@app.get("/places/autocomplete")
def places_autocomplete_get(
    input: str | None = None,
    text: str | None = None,
    sessiontoken: str | None = None,
    components: str | None = None,
):
    """
    Supports:
      /places/autocomplete?input=Austin
      /places/autocomplete?text=Austin

    Returns:
      {"predictions":[{"description":"Austin, TX, USA","place_id":"...","types":[...]}]}
    """
    if not GOOGLE_API_KEY:
        raise HTTPException(status_code=500, detail="Missing GOOGLE_MAPS_API_KEY")

    q = (input or text or "").strip()
    if not q:
        raise HTTPException(status_code=400, detail="Missing input")

    url = "https://places.googleapis.com/v1/places:autocomplete"

    body: dict = {
        "input": q,
        "includedPrimaryTypes": [
            "locality",
            "administrative_area_level_1",
            "administrative_area_level_2",
        ],
    }

    if components and "country:" in components:
        try:
            body["regionCode"] = components.split("country:", 1)[1].strip().upper()
        except Exception:
            pass

    if sessiontoken:
        body["sessionToken"] = sessiontoken

    field_mask = (
        "suggestions.placePrediction.placeId,"
        "suggestions.placePrediction.types,"
        "suggestions.placePrediction.text,"
        "suggestions.placePrediction.structuredFormat"
    )

    data = _places_new_post(url, body, field_mask=field_mask)
    suggestions = data.get("suggestions", []) or []

    preds = []
    for s in suggestions:
        pp = s.get("placePrediction") or {}
        place_id = pp.get("placeId")
        types = pp.get("types") or []

        sf = pp.get("structuredFormat") or {}
        main = ((sf.get("mainText") or {}).get("text") or "").strip()
        secondary = ((sf.get("secondaryText") or {}).get("text") or "").strip()

        if main and secondary:
            desc = f"{main}, {secondary}"
        else:
            desc = ((pp.get("text") or {}).get("text") or "").strip()

        if place_id and desc:
            preds.append({"description": desc, "place_id": place_id, "types": types})

    return {"predictions": preds}


class AutocompleteBody(BaseModel):
    input: Optional[str] = None
    text: Optional[str] = None
    sessiontoken: Optional[str] = None
    components: Optional[str] = None


@app.post("/places/autocomplete")
def places_autocomplete_post(payload: AutocompleteBody = Body(...)):
    """POST variant so frontend can also send JSON."""
    return places_autocomplete_get(
        input=payload.input,
        text=payload.text,
        sessiontoken=payload.sessiontoken,
        components=payload.components,
    )


# -------------------------------------------------
# /places/details
# -------------------------------------------------
@app.get("/places/details")
def place_details(place_id: str, sessiontoken: str | None = None):
    """Fetch details (name/address/lat/lng) for a place_id."""
    if not GOOGLE_API_KEY:
        raise HTTPException(status_code=500, detail="Missing GOOGLE_MAPS_API_KEY")
    if not place_id:
        raise HTTPException(status_code=400, detail="Missing place_id")

    field_mask = "id,displayName,formattedAddress,location,types"
    url = f"https://places.googleapis.com/v1/places/{place_id}"

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


# -------------------------------------------------
# /places/resolve (text → place_id + lat/lng)
# -------------------------------------------------
class ResolvePlaceRequest(BaseModel):
    text: str
    sessiontoken: Optional[str] = None


@app.post("/places/resolve")
def resolve_place(payload: ResolvePlaceRequest = Body(...)):
    """Resolve a free-text place string into a canonical place_id + lat/lng."""
    if not GOOGLE_API_KEY:
        raise HTTPException(status_code=500, detail="Missing GOOGLE_MAPS_API_KEY")

    text = payload.text
    sessiontoken = payload.sessiontoken

    url = "https://places.googleapis.com/v1/places:searchText"
    field_mask = "places.id,places.displayName,places.formattedAddress,places.location,places.types"

    body: dict = {"textQuery": text}
    if sessiontoken:
        body["sessionToken"] = sessiontoken

    data = _places_new_post(url, body, field_mask=field_mask)
    places = data.get("places", []) or []
    if not places:
        return {"status": "ZERO_RESULTS", "query": text, "place": None}

    top = places[0] or {}
    place_id = top.get("id")
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


# -------------------------------------------------
# Internal helper: resolve a stop title to lat/lng (prevents map from guessing wrong place)
# -------------------------------------------------
def _resolve_stop_title(title: str, bias_lat: float | None = None, bias_lng: float | None = None) -> Dict[str, Any] | None:
    """Resolve a stop title to a canonical place with lat/lng using Places searchText.

    Uses an optional locationBias circle when bias coords are provided (strongly reduces wrong matches).
    Returns a dict with keys: place_id, name, formatted_address, lat, lng, types.
    """
    if not GOOGLE_API_KEY:
        return None

    q = (title or "").strip()
    if not q:
        return None

    url = "https://places.googleapis.com/v1/places:searchText"
    field_mask = "places.id,places.displayName,places.formattedAddress,places.location,places.types"

    body: Dict[str, Any] = {"textQuery": q}

    # Bias the search near destination to avoid resolving to a similarly-named place far away (e.g., Oregon)
    if bias_lat is not None and bias_lng is not None:
        body["locationBias"] = {
            "circle": {
                "center": {"latitude": float(bias_lat), "longitude": float(bias_lng)},
                "radius": 75000.0,  # ~46 miles
            }
        }

    data = _places_new_post(url, body, field_mask=field_mask)
    places = data.get("places") or []
    if not places:
        return None

    top = places[0] or {}
    loc = top.get("location") or {}
    name = (top.get("displayName") or {}).get("text")

    if loc.get("latitude") is None or loc.get("longitude") is None:
        return None

    return {
        "place_id": top.get("id"),
        "name": name,
        "formatted_address": top.get("formattedAddress"),
        "lat": loc.get("latitude"),
        "lng": loc.get("longitude"),
        "types": top.get("types", []),
    }


# -------------------------------------------------
# Distance / duration helpers
# -------------------------------------------------
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
    if not dur or not isinstance(dur, str):
        return None
    if dur.endswith("s"):
        try:
            return int(float(dur[:-1]))
        except Exception:
            return None
    return None


# -------------------------------------------------
# Polyline + geo helpers
# -------------------------------------------------
MILES_20_M = 32187.0
MILES_30_M = 48280.0


def _haversine_m(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 6371000.0
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlng / 2) ** 2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _decode_polyline(encoded: str) -> List[Dict[str, float]]:
    """Decode Google encoded polyline to a list of {lat,lng}."""
    if not encoded:
        return []
    idx = 0
    lat = 0
    lng = 0
    coords: List[Dict[str, float]] = []

    while idx < len(encoded):
        shift = 0
        result = 0
        while True:
            b = ord(encoded[idx]) - 63
            idx += 1
            result |= (b & 0x1F) << shift
            shift += 5
            if b < 0x20:
                break
        dlat = ~(result >> 1) if (result & 1) else (result >> 1)
        lat += dlat

        shift = 0
        result = 0
        while True:
            b = ord(encoded[idx]) - 63
            idx += 1
            result |= (b & 0x1F) << shift
            shift += 5
            if b < 0x20:
                break
        dlng = ~(result >> 1) if (result & 1) else (result >> 1)
        lng += dlng

        coords.append({"lat": lat / 1e5, "lng": lng / 1e5})

    return coords


def _sample_route_points(path: List[Dict[str, float]], step_m: float = 20000.0, max_points: int = 8) -> List[Dict[str, float]]:
    """Sample points along a polyline every ~step_m meters, capped at max_points."""
    if not path:
        return []

    sampled = [path[0]]
    acc = 0.0

    for i in range(1, len(path)):
        a = path[i - 1]
        b = path[i]
        acc += _haversine_m(a["lat"], a["lng"], b["lat"], b["lng"])
        if acc >= step_m:
            sampled.append(b)
            acc = 0.0
            if len(sampled) >= max_points:
                break

    if len(sampled) < max_points and (path[-1] != sampled[-1]):
        sampled.append(path[-1])

    return sampled[:max_points]


def _point_at_distance(path: List[Dict[str, float]], target_m: float) -> Dict[str, float] | None:
    """Return the lat/lng point along `path` at approximately `target_m` meters from the start."""
    if not path:
        return None
    if target_m <= 0:
        return path[0]

    traveled = 0.0
    for i in range(1, len(path)):
        a = path[i - 1]
        b = path[i]
        seg = _haversine_m(a["lat"], a["lng"], b["lat"], b["lng"])

        if traveled + seg >= target_m:
            remain = target_m - traveled
            t = 0.0 if seg == 0 else max(0.0, min(1.0, remain / seg))
            return {
                "lat": a["lat"] + (b["lat"] - a["lat"]) * t,
                "lng": a["lng"] + (b["lng"] - a["lng"]) * t,
            }

        traveled += seg

    return path[-1]


# -------------------------------------------------
# Pydantic models used by routes
# -------------------------------------------------
class LatLng(BaseModel):
    lat: float
    lng: float
    place_id: Optional[str] = None


class RoutesRequest(BaseModel):
    start: LatLng
    destination: LatLng
    waypoints: List[LatLng] = []


class AlternativesRequest(BaseModel):
    start: LatLng
    destination: LatLng
    interests: List[str] = []


class ThingsToDoRequest(BaseModel):
    start: LatLng
    destination: LatLng
    mood: Optional[str] = "scenic"
    limit: Optional[int] = 12
    destination_query: Optional[str] = None  # e.g., "Austin, TX" (reserved for future web search)

class MidStop(BaseModel):
    title: str
    lat: Optional[float] = None
    lng: Optional[float] = None


class PlanTripRequest(BaseModel):
    start_city: Optional[str] = None
    destination: Optional[str] = None
    days: Optional[int] = 1

    stop_b_title: Optional[str] = None
    stop_b_lat: Optional[float] = None
    stop_b_lng: Optional[float] = None

    pace: Optional[str] = None
    destination_state: Optional[str] = None
    interests: Optional[List[str]] = None
    group: Optional[Dict[str, Any]] = None
    start_lat: Optional[float] = None
    start_lng: Optional[float] = None
    destination_lat: Optional[float] = None
    destination_lng: Optional[float] = None

    mid_stops: Optional[List[MidStop]] = None


# -------------------------------------------------
# /routes → Google Routes API (DRIVE)
# -------------------------------------------------
@app.post("/routes")
def routes(req: RoutesRequest):
    """Return a driving route polyline + distance/duration."""
    if not GOOGLE_API_KEY:
        raise HTTPException(status_code=500, detail="Missing GOOGLE_MAPS_API_KEY")

    url = "https://routes.googleapis.com/directions/v2:computeRoutes"

    body: Dict[str, Any] = {
        "origin": {"location": {"latLng": {"latitude": req.start.lat, "longitude": req.start.lng}}},
        "destination": {"location": {"latLng": {"latitude": req.destination.lat, "longitude": req.destination.lng}}},
        "travelMode": "DRIVE",
        "routingPreference": "TRAFFIC_AWARE",
        "computeAlternativeRoutes": False,
    }

    if req.waypoints:
        # Do NOT set `via: true` here. Via points may not create separate legs.
        # We want per-stop legs so the frontend can show segment times/distances.
        body["intermediates"] = [
            {
                "location": {"latLng": {"latitude": w.lat, "longitude": w.lng}},
            }
            for w in req.waypoints
        ]

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_API_KEY,
        # Include legs so frontend can show per-segment time/distance without extra API calls
        "X-Goog-FieldMask": (
            "routes.distanceMeters,"
            "routes.duration,"
            "routes.polyline.encodedPolyline,"
            "routes.legs,"
            "routes.legs.distanceMeters,"
            "routes.legs.duration,"
            "routes.legs.startLocation,"
            "routes.legs.endLocation"
        ),
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

    legs_out: List[Dict[str, Any]] = []
    for lg in (rt.get("legs") or []):
        lg_dist_m = lg.get("distanceMeters")
        lg_dur_s = _parse_duration_to_seconds(lg.get("duration"))
        legs_out.append(
            {
                "distance_meters": lg_dist_m,
                "duration_seconds": lg_dur_s,
                "distance_text": _format_distance_meters(lg_dist_m),
                "duration_text": _format_duration_seconds(lg_dur_s),
            }
        )

    return {
        "polyline": poly,
        "distance_meters": dist_m,
        "duration_seconds": dur_s,
        "distance_text": _format_distance_meters(dist_m),
        "duration_text": _format_duration_seconds(dur_s),
        "legs": legs_out,
    }


# -------------------------------------------------
# /places/alternatives → one nice midpoint stop
# -------------------------------------------------
@app.post("/places/alternatives")
def places_alternatives(req: AlternativesRequest):
    """Return one suggested stop near the midpoint between start and destination."""
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

    if not included:
        included = ["tourist_attraction"]

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


# -------------------------------------------------
# /places/things-to-do → route-aware "Things to do"
# -------------------------------------------------
@app.post("/places/things-to-do")
def places_things_to_do(req: ThingsToDoRequest):
    """Route-aware 'Things to do' recommendations.

    Option A (Places-only for now):
      - en_route: around ~45–60 minutes from the start (avoids Dallas dominating early)
      - near_destination: around last ~20–30 minutes before destination (Austin-focused)

    SerpAPI/web-search is intentionally disabled for now.
    """

    if not GOOGLE_API_KEY:
        raise HTTPException(status_code=500, detail="Missing GOOGLE_MAPS_API_KEY")

    mood = (req.mood or "scenic").strip().lower()
    limit = int(req.limit or 12)
    limit = max(1, min(limit, 30))

    mood_types: Dict[str, List[str]] = {
        "hiking": ["park", "campground", "tourist_attraction"],
        "scenic": ["tourist_attraction", "park", "point_of_interest"],
        "food": ["restaurant", "cafe", "bakery"],
        "photo": ["tourist_attraction", "park", "museum"],
        "culture": ["museum", "art_gallery", "tourist_attraction"],
        "adventure": ["amusement_park", "tourist_attraction", "park"],
        "relax": ["spa", "park", "tourist_attraction"],
    }
    included_types = mood_types.get(mood, ["tourist_attraction", "park"])
    included_types = list(dict.fromkeys(included_types))[:3]

    # 1) get route polyline (A → C)
    route = routes(RoutesRequest(start=req.start, destination=req.destination, waypoints=[]))
    poly = route.get("polyline")
    if not poly:
        raise HTTPException(status_code=502, detail="Routes API did not return a polyline")

    path = _decode_polyline(poly)
    if len(path) < 2:
        raise HTTPException(status_code=502, detail="Routes API polyline could not be decoded")

    dur_s = route.get("duration_seconds")

    # compute total length
    total_len = 0.0
    for i in range(1, len(path)):
        a = path[i - 1]
        b = path[i]
        total_len += _haversine_m(a["lat"], a["lng"], b["lat"], b["lng"])

    # --- Bucket A: en_route (~45–60 min from start)
    if dur_s and dur_s > 0 and total_len > 0:
        low_m = total_len * min(1.0, 2700.0 / float(dur_s))   # 45 min
        high_m = total_len * min(1.0, 3600.0 / float(dur_s))  # 60 min
    else:
        low_m = total_len * 0.40
        high_m = total_len * 0.50

    anchor_low = _point_at_distance(path, low_m) or path[0]
    anchor_high = _point_at_distance(path, high_m) or path[0]

    # --- Bucket B: near_destination (last ~20–30 min before destination)
    if dur_s and dur_s > 0 and total_len > 0:
        dest_low_m = total_len * max(0.0, min(1.0, (float(dur_s) - 1800.0) / float(dur_s)))  # -30 min
        dest_high_m = total_len * max(0.0, min(1.0, (float(dur_s) - 1200.0) / float(dur_s))) # -20 min
    else:
        dest_low_m = total_len * 0.85
        dest_high_m = total_len * 0.92

    anchor_dest_low = _point_at_distance(path, dest_low_m) or path[-1]
    anchor_dest_high = _point_at_distance(path, dest_high_m) or path[-1]

    url = "https://places.googleapis.com/v1/places:searchNearby"
    field_mask = (
        "places.id,places.displayName,places.formattedAddress,places.location,"
        "places.types,places.rating,places.userRatingCount"
    )

    found_en_route: Dict[str, Dict[str, Any]] = {}
    found_near_dest: Dict[str, Dict[str, Any]] = {}

    def add_places(found: Dict[str, Dict[str, Any]], lat: float, lng: float, radius_m: float, max_count: int = 12):
        body = {
            "includedTypes": included_types,
            "maxResultCount": max_count,
            "locationRestriction": {
                "circle": {
                    "center": {"latitude": lat, "longitude": lng},
                    "radius": float(radius_m),
                }
            },
        }
        data = _places_new_post(url, body, field_mask=field_mask)
        for p in (data.get("places") or []):
            pid = p.get("id")
            if pid:
                found[pid] = p

    # En-route: keep your strict Dallas-avoid rule
    add_places(found_en_route, anchor_low["lat"], anchor_low["lng"], MILES_20_M, max_count=15)
    add_places(found_en_route, anchor_high["lat"], anchor_high["lng"], MILES_20_M, max_count=15)

    # Near destination: smaller radius so Austin-side dominates
    near_dest_radius = 24000.0  # ~15 miles
    add_places(found_near_dest, anchor_dest_low["lat"], anchor_dest_low["lng"], near_dest_radius, max_count=15)
    add_places(found_near_dest, anchor_dest_high["lat"], anchor_dest_high["lng"], near_dest_radius, max_count=15)

    def score(p: Dict[str, Any]) -> float:
        rating = float(p.get("rating") or 0.0)
        votes = float(p.get("userRatingCount") or 0.0)
        return rating * math.log(votes + 1.0)

    def normalize(p: Dict[str, Any]) -> Dict[str, Any]:
        loc = p.get("location") or {}
        name = (p.get("displayName") or {}).get("text")
        return {
            "place_id": p.get("id"),
            "title": name,
            "formatted_address": p.get("formattedAddress"),
            "lat": loc.get("latitude"),
            "lng": loc.get("longitude"),
            "types": p.get("types") or [],
            "rating": p.get("rating"),
            "votes": p.get("userRatingCount"),
        }

    ranked_en_route = sorted(found_en_route.values(), key=score, reverse=True)
    ranked_near_dest = sorted(found_near_dest.values(), key=score, reverse=True)

    en_route_out = [normalize(p) for p in ranked_en_route[:limit]]
    near_dest_out = [normalize(p) for p in ranked_near_dest[:limit]]

    # Deduplicate across buckets (prefer near_destination)
    seen: set[str] = set()
    dedup_near: List[Dict[str, Any]] = []
    for p in near_dest_out:
        pid = p.get("place_id")
        if pid and pid not in seen:
            seen.add(pid)
            dedup_near.append(p)

    dedup_en: List[Dict[str, Any]] = []
    for p in en_route_out:
        pid = p.get("place_id")
        if pid and pid not in seen:
            seen.add(pid)
            dedup_en.append(p)

    return {
        "mood": mood,
        "en_route": dedup_en,
        "near_destination": dedup_near,
        "count": {"en_route": len(dedup_en), "near_destination": len(dedup_near)},
        "used_web_search": False,
    }


# -------------------------------------------------
# /plan-trip → simple itinerary object for Stage 4
# -------------------------------------------------
@app.post("/plan-trip")
def plan_trip(req: PlanTripRequest = Body(...)):
    """Minimal MVP itinerary builder for Stage 4."""

    start_city = (req.start_city or "Start").strip() or "Start"
    dest_city = (req.destination or "Destination").strip() or "Destination"

    n_days = int(req.days or 1)
    if n_days < 1:
        n_days = 1
    if n_days > 30:
        n_days = 30

    # Safety cap: too many mid-stops makes itineraries messy and can break downstream routing.
    # Frontend can allow fewer; backend enforces a hard max.
    MAX_MID_STOPS = 8
    if req.mid_stops and len(req.mid_stops) > MAX_MID_STOPS:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {MAX_MID_STOPS} mid-stops allowed. You sent {len(req.mid_stops)}.",
        )

    # Build Start stop (include lat/lng so Stage 4 map can plot it)
    start_stop: Dict[str, Any] = {"title": start_city}
    if req.start_lat is not None and req.start_lng is not None:
        start_stop["lat"] = req.start_lat
        start_stop["lng"] = req.start_lng
    else:
        resolved_start = _resolve_stop_title(start_city)
        if resolved_start:
            start_stop["lat"] = resolved_start.get("lat")
            start_stop["lng"] = resolved_start.get("lng")
            if resolved_start.get("place_id"):
                start_stop["place_id"] = resolved_start.get("place_id")
            if resolved_start.get("formatted_address"):
                start_stop["formatted_address"] = resolved_start.get("formatted_address")

    stops_day1: List[Dict[str, Any]] = [start_stop]

    # Prefer the new mid_stops array if the frontend sends it
    if req.mid_stops:
        for ms in req.mid_stops:
            title = (ms.title or "").strip()
            if not title:
                continue

            stop_obj: Dict[str, Any] = {"title": title, "stay": "1 hr"}

            # If frontend provided coordinates, trust them.
            if ms.lat is not None and ms.lng is not None:
                stop_obj["lat"] = ms.lat
                stop_obj["lng"] = ms.lng
            else:
                # Otherwise, resolve the title using Places, biased near destination to prevent wrong far-away matches.
                resolved = _resolve_stop_title(title, bias_lat=req.destination_lat, bias_lng=req.destination_lng)
                if resolved:
                    stop_obj["lat"] = resolved.get("lat")
                    stop_obj["lng"] = resolved.get("lng")
                    if resolved.get("place_id"):
                        stop_obj["place_id"] = resolved.get("place_id")
                    if resolved.get("formatted_address"):
                        stop_obj["formatted_address"] = resolved.get("formatted_address")

            stops_day1.append(stop_obj)

    # Backwards-compatible: fall back to the old single B-stop fields
    elif req.stop_b_title and req.stop_b_title.strip():
        sb_title = req.stop_b_title.strip()
        sb: Dict[str, Any] = {"title": sb_title, "stay": "1 hr"}

        if req.stop_b_lat is not None and req.stop_b_lng is not None:
            sb["lat"] = req.stop_b_lat
            sb["lng"] = req.stop_b_lng
        else:
            resolved = _resolve_stop_title(sb_title, bias_lat=req.destination_lat, bias_lng=req.destination_lng)
            if resolved:
                sb["lat"] = resolved.get("lat")
                sb["lng"] = resolved.get("lng")
                if resolved.get("place_id"):
                    sb["place_id"] = resolved.get("place_id")
                if resolved.get("formatted_address"):
                    sb["formatted_address"] = resolved.get("formatted_address")

        stops_day1.append(sb)

    # Always end Day 1 at the destination (include lat/lng so Stage 4 map can plot it)
    dest_stop: Dict[str, Any] = {"title": dest_city}
    if req.destination_lat is not None and req.destination_lng is not None:
        dest_stop["lat"] = req.destination_lat
        dest_stop["lng"] = req.destination_lng
    else:
        resolved_dest = _resolve_stop_title(dest_city)
        if resolved_dest:
            dest_stop["lat"] = resolved_dest.get("lat")
            dest_stop["lng"] = resolved_dest.get("lng")
            if resolved_dest.get("place_id"):
                dest_stop["place_id"] = resolved_dest.get("place_id")
            if resolved_dest.get("formatted_address"):
                dest_stop["formatted_address"] = resolved_dest.get("formatted_address")

    stops_day1.append(dest_stop)

    days = []
    for d in range(n_days):
        if d == 0:
            days.append({"day": 1, "stops": stops_day1})
        else:
            days.append({"day": d + 1, "stops": [{"title": dest_city}]})

    summary = f"Trip from {start_city} to {dest_city} for {n_days} day{'s' if n_days != 1 else ''}."

    # Prefer mid_stops in the summary if present
    if req.mid_stops:
        names = [(ms.title or "").strip() for ms in req.mid_stops if (ms.title or "").strip()]
        if names:
            mid_phrase = ", ".join(names)
            if len(names) == 1:
                summary = (
                    f"Trip from {start_city} to {dest_city} with a stop at {mid_phrase} "
                    f"for {n_days} day{'s' if n_days != 1 else ''}."
                )
            else:
                summary = (
                    f"Trip from {start_city} to {dest_city} with stops at {mid_phrase} "
                    f"for {n_days} day{'s' if n_days != 1 else ''}."
                )

    # Fallback: old single B-stop behavior
    elif req.stop_b_title and req.stop_b_title.strip():
        summary = (
            f"Trip from {start_city} to {dest_city} with a stop at {req.stop_b_title.strip()} "
            f"for {n_days} day{'s' if n_days != 1 else ''}."
        )
        
    return {
        "summary": summary,
        "start_city": start_city,
        "destination": dest_city,
        "days": days,
        "start": {"title": start_city, "lat": start_stop.get("lat"), "lng": start_stop.get("lng"), "place_id": start_stop.get("place_id")},
        "destination_obj": {"title": dest_city, "lat": dest_stop.get("lat"), "lng": dest_stop.get("lng"), "place_id": dest_stop.get("place_id")},
    }


# -------------------------------------------------
# Include legacy router (trip.py)
# -------------------------------------------------
from .routes.trip import router as trip_router
app.include_router(trip_router)
