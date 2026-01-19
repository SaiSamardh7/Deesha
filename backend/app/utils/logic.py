from __future__ import annotations

from typing import List


def normalize_text(s: str) -> str:
    return (s or "").strip()


def pick_mid_stop(interests: List[str]) -> str:
    interests = [i.lower().strip() for i in (interests or [])]

    if "adventure" in interests or "hiking" in interests:
        return "Scenic trail viewpoint"
    if "photography" in interests or "photo" in interests:
        return "Golden hour photo spot"
    if "food" in interests:
        return "Famous local eats"
    if "hidden gems" in interests or "hidden" in interests:
        return "Hidden gem detour"

    return "Optional quick stop"
