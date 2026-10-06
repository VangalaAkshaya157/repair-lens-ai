from __future__ import annotations

import os
from typing import Any


UNAVAILABLE_MESSAGE = "Verified current repair pricing is unavailable."


def get_repair_price(*, device_category: str, brand: str, model: str, component: str) -> dict[str, Any]:
    """Return only verified provider data; no prices are fabricated locally."""
    if not os.getenv("REPAIR_PRICE_API_URL", "").strip():
        return {"estimated_cost": UNAVAILABLE_MESSAGE, "price_confidence": "Unavailable", "price_sources": []}
    # A provider adapter can be added here once a legitimate pricing API is configured.
    return {"estimated_cost": UNAVAILABLE_MESSAGE, "price_confidence": "Unavailable", "price_sources": []}
