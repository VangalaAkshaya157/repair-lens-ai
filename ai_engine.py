from __future__ import annotations

import json
import os
import re
from typing import Any

from dotenv import load_dotenv

load_dotenv()

DEMO_MESSAGE = "Demo Mode – Gemini AI is not currently connected."
MODEL_NAME = "gemini-2.5-flash"
INSUFFICIENT_EVIDENCE_MESSAGE = "Please describe the problem or upload an image before starting the analysis."
MEANINGLESS_DESCRIPTIONS = {
    "nothing", "ntg", "none", "no", "idk", "i don't know", "dont know",
    "don't know", "problem", "issue", "broken",
}


def has_useful_description(description: str) -> bool:
    normalized = " ".join(description.lower().strip().split())
    if not normalized or normalized in MEANINGLESS_DESCRIPTIONS:
        return False
    return len(normalized) >= 8 and any(character.isalpha() for character in normalized)


def generate_demo_diagnosis(device_category: str, problem_description: str) -> dict[str, Any]:
    """Provide a realistic local assessment when Gemini is unavailable."""
    text = problem_description.lower()
    if any(word in text for word in ("screen", "display", "crack", "glass")):
        problem, causes, cost = (
            "Display or screen assembly damage",
            ["Physical impact may have damaged the display panel", "A loose display connector is possible"],
            "₹6,000 – ₹14,000",
        )
    elif any(word in text for word in ("battery", "charge", "charging", "power")):
        problem, causes, cost = (
            "Battery or charging circuit issue",
            ["Battery health may be degraded", "The charging port or cable may be damaged"],
            "₹2,000 – ₹7,000",
        )
    elif any(word in text for word in ("water", "liquid", "spill")):
        problem, causes, cost = (
            "Possible liquid ingress damage",
            ["Moisture may have reached internal components", "Corrosion may develop over time"],
            "₹3,000 – ₹12,000",
        )
    elif any(word in text for word in ("slow", "hang", "freeze", "restart")):
        problem, causes, cost = (
            "Performance or software instability",
            ["Background software may be consuming resources", "Storage or system files may need attention"],
            "₹1,000 – ₹4,000",
        )
    else:
        problem, causes, cost = (
            f"General {device_category.lower()} hardware or software issue",
            ["The symptoms are not specific enough to isolate one component", "A professional inspection may be needed"],
            "₹2,000 – ₹8,000",
        )
    repair_or_replace = "Replace" if "₹6,000" in cost or "₹12,000" in cost else "Repair"
    return {
        "possible_problem": problem,
        "possible_causes": causes,
        "confidence": "Medium",
        "confidence_score": 72,
        "estimated_cost": cost,
        "estimated_repair_time": "1–3 business days",
        "repair_or_replace": repair_or_replace,
        "repair_reason": "Repair is generally reasonable based on the available symptoms and estimated range.",
        "troubleshooting_steps": [
            "Back up important data if the device is still usable.",
            "Power the device off and avoid using it if it is hot, wet, swollen, or producing unusual smells.",
            "Check the manufacturer-approved cable, power source, or restart procedure.",
        ],
        "safety_warning": "Do not open the device or handle internal components. Stop using it if there is heat, smoke, swelling, liquid, or a burning smell.",
        "professional_help": "Consult a qualified repair professional if the issue continues or involves internal components.",
    }


def _prompt(device_category: str, brand: str, model: str, problem_description: str) -> str:
    return f"""
You are RepairLens AI, a cautious device repair decision assistant.
Assess the following device using the description and, when supplied, the attached image.
Your response is an estimate of POSSIBLE causes, never a guaranteed technical diagnosis.
Never provide dangerous instructions involving high voltage, exposed wiring, batteries,
gas appliances, refrigerants, dangerous chemicals, unsafe disassembly, or complex vehicle repairs.
For those situations, give safe stop-use advice and recommend a qualified professional.
Use Indian rupees for cost ranges and do not invent an exact price.

Device category: {device_category}
Brand: {brand or "Unknown"}
Model: {model or "Unknown"}
Problem description: {problem_description or "No description supplied. Assess the attached image only."}

Return ONLY valid JSON with exactly these keys:
{{
  "visible_evidence": ["Only what is visibly supported by the image"],
  "user_reported_symptoms": ["Only what the user reported"],
  "uncertainties": ["What cannot be confirmed from the available evidence"],
  "possible_problem": "possible problem, never a confirmed diagnosis",
  "likely_component": "likely component or unknown",
  "possible_causes": ["possible causes supported by the evidence"],
  "confidence": "Low, Medium, High, or Very low",
  "confidence_score": 0,
  "estimated_repair_time": "string",
  "repair_or_replace": "Repair, Replace, or Professional assessment",
  "repair_reason": "string",
  "troubleshooting_steps": ["safe string"],
  "safety_warning": "string",
  "professional_help": "string"
}}
The confidence score must be an integer percentage from 0 to 100.
"""


def _normalize_result(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError("Gemini response was not an object")
    required = ("possible_problem", "possible_causes", "confidence", "confidence_score",
                "estimated_repair_time", "repair_or_replace", "repair_reason",
                "troubleshooting_steps", "safety_warning", "professional_help")
    if any(key not in value for key in required):
        raise ValueError("Gemini response was missing required fields")
    result = dict(value)
    result["visible_evidence"] = [str(item) for item in value.get("visible_evidence", [])][:8]
    result["user_reported_symptoms"] = [str(item) for item in value.get("user_reported_symptoms", [])][:8]
    result["uncertainties"] = [str(item) for item in value.get("uncertainties", [])][:8]
    result["possible_causes"] = [str(item) for item in result["possible_causes"]][:8]
    result["troubleshooting_steps"] = [str(item) for item in result["troubleshooting_steps"]][:8]
    result["confidence_score"] = max(0, min(100, int(float(result["confidence_score"]))))
    result["likely_component"] = str(value.get("likely_component", "Unknown component"))
    result["estimated_cost"] = str(value.get("estimated_cost", "Verified current repair pricing is unavailable."))
    for key in ("possible_problem", "confidence", "estimated_repair_time",
                "repair_or_replace", "repair_reason", "safety_warning", "professional_help"):
        result[key] = str(result[key])
    return result


def _structured_from_demo(device_category: str, problem_description: str, image_available: bool) -> dict[str, Any]:
    legacy = generate_demo_diagnosis(device_category, problem_description or "image inspection")
    description_available = has_useful_description(problem_description)
    if image_available and description_available:
        basis, confidence, score = "description_and_image", "Medium", 72
    elif image_available:
        basis, confidence, score = "image_only", "Low", 52
    else:
        basis, confidence, score = "description_only", "Medium", 62
    legacy.update({
        "visible_evidence": ["The uploaded image was received for inspection."] if image_available else [],
        "user_reported_symptoms": [problem_description] if description_available else [],
        "uncertainties": ["Internal damage cannot be confirmed without professional inspection."],
        "likely_component": "Device component related to the reported symptoms",
        "confidence": confidence,
        "confidence_score": score,
        "estimated_cost": "Verified current repair pricing is unavailable.",
        "price_confidence": "Unavailable",
        "analysis_basis": basis,
        "price_sources": [],
        "nearby_shops": [],
    })
    return legacy


def generate_evidence_diagnosis(
    device_category: str,
    brand: str,
    model: str,
    problem_description: str,
    image_bytes: bytes | None = None,
    image_mime_type: str | None = None,
) -> tuple[dict[str, Any], bool]:
    """Generate an evidence-aware assessment; configured Gemini failures are raised for honest API errors."""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return _structured_from_demo(device_category, problem_description, bool(image_bytes)), True
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    contents: list[Any] = [_prompt(device_category, brand, model, problem_description)]
    if image_bytes:
        contents.append(types.Part.from_bytes(data=image_bytes, mime_type=image_mime_type or "image/jpeg"))
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=contents,
        config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.2),
    )
    raw_text = re.sub(r"^```(?:json)?\s*|\s*```$", "", (response.text or "").strip(), flags=re.IGNORECASE)
    result = _normalize_result(json.loads(raw_text))
    result["analysis_basis"] = (
        "description_and_image" if image_bytes and has_useful_description(problem_description)
        else "image_only" if image_bytes else "description_only"
    )
    result["price_confidence"] = "Unavailable"
    result["price_sources"] = []
    result["nearby_shops"] = []
    result["estimated_cost"] = "Verified current repair pricing is unavailable."
    return result, False


def generate_diagnosis(
    device_category: str,
    brand: str,
    model: str,
    problem_description: str,
    image_bytes: bytes | None = None,
    image_mime_type: str | None = None,
) -> tuple[dict[str, Any], bool]:
    """Call Gemini and return (assessment, used_demo_mode). Any integration failure falls back safely."""
    try:
        return generate_evidence_diagnosis(
            device_category, brand, model, problem_description, image_bytes, image_mime_type
        )
    except Exception:
        return _structured_from_demo(device_category, problem_description, bool(image_bytes)), True
