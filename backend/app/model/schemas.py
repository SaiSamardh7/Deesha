from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel


class Group(BaseModel):
    adults: int = 1
    kids: int = 0


class TripRequest(BaseModel):
    start_city: str
    destination: str
    destination_state: Optional[str] = None
    days: int = 3
    pace: Optional[str] = "balanced"
    group: Optional[Group] = None
    interests: Optional[List[str]] = None


class Stop(BaseModel):
    title: str
    category: str


class DayPlan(BaseModel):
    day: int
    title: str
    stops: List[Stop]


class TripResponse(BaseModel):
    summary: str
    start_city: str
    destination: str
    destination_state: str
    days: List[DayPlan]
