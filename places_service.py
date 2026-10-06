from __future__ import annotations

import os
from typing import Any


UNAVAILABLE_MESSAGE = "Nearby repair-shop information is currently unavailable."


def find_nearby_shops(*, device_category: str, brand: str, location: str) -> dict[str, Any]:
    """Return only businesses from a configured legitimate places provider."""
    if not os.getenv("PLACES_API_URL", "").strip() or not location.strip():
        return {"nearby_shops": [], "message": UNAVAILABLE_MESSAGE}
    # A provider adapter can be added here once a legitimate places API is configured.
    return {"nearby_shops": [], "message": UNAVAILABLE_MESSAGE}
