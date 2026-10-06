from __future__ import annotations

from flask import Flask, jsonify, render_template, request

from ai_engine import generate_evidence_diagnosis, has_useful_description
from database import create_diagnosis, get_session
from places_service import find_nearby_shops
from price_service import get_repair_price


app = Flask(__name__)


@app.get("/")
def dashboard():
    return render_template("index.html", active_page="dashboard")


@app.get("/diagnose")
def diagnose():
    return render_template("diagnose.html", active_page="diagnose")


@app.get("/cost-estimator")
def cost_estimator():
    return render_template("cost_estimator.html", active_page="cost-estimator")


@app.get("/history")
def history():
    return render_template("history.html", active_page="history")


@app.get("/about")
def about():
    return render_template("about.html", active_page="about")


def _estimated_cost_value(cost_text: object) -> float:
    import re

    values = [float(value.replace(",", "")) for value in re.findall(r"[\d,]+", str(cost_text))]
    return sum(values) / len(values) if values else 0.0


@app.post("/api/diagnose")
def api_diagnose():
    app.logger.info("Diagnosis request received")
    image = request.files.get("image")
    image_bytes = image.read() if image and image.filename else None
    app.logger.info("Image received: %s", "yes" if image_bytes else "no")

    device_category = request.form.get("device_category", "").strip()
    brand = request.form.get("brand", "").strip()
    model = request.form.get("model", "").strip()
    problem_description = request.form.get("problem_description", request.form.get("problem", "")).strip()
    if not device_category:
        return jsonify(success=False, error="Please select a device category."), 400
    if not brand:
        return jsonify(success=False, error="Please enter the device brand."), 400
    if not model:
        return jsonify(success=False, error="Please enter the device model."), 400
    if not has_useful_description(problem_description):
        return jsonify(success=False, error="Please describe the problem." if not problem_description else "Please provide a more detailed description of the problem."), 400
    if not image_bytes:
        return jsonify(success=False, error="Please upload an image of the device or damaged area."), 400
    if image_bytes and len(image_bytes) > 10 * 1024 * 1024:
        return jsonify(success=False, error="This image is too large. Please upload an image under 10 MB."), 400
    if image_bytes and (not image.mimetype or not image.mimetype.startswith("image/")):
        return jsonify(success=False, error="We couldn't process this image. Please upload a clear image and try again."), 400
    if image_bytes:
        try:
            from PIL import Image

            with Image.open(__import__("io").BytesIO(image_bytes)) as uploaded_image:
                uploaded_image.verify()
        except Exception:
            return jsonify(success=False, error="We couldn't process this image. Please upload a clear image and try again."), 400

    try:
        app.logger.info("Calling AI engine")
        result, demo_mode = generate_evidence_diagnosis(
            device_category=device_category,
            brand=brand,
            model=model,
            problem_description=problem_description,
            image_bytes=image_bytes,
            image_mime_type=image.mimetype if image and image.filename else None,
        )
        app.logger.info("AI response received (mode=%s)", "demo" if demo_mode else "gemini")
        price = get_repair_price(
            device_category=device_category,
            brand=brand,
            model=model,
            component=result.get("likely_component", ""),
        )
        shops = find_nearby_shops(device_category=device_category, brand=brand, location=request.form.get("location", ""))
        result.update(price)
        result["nearby_shops"] = shops["nearby_shops"]
        result["nearby_shops_message"] = shops["message"]

        app.logger.info("Saving diagnosis")
        with get_session() as session:
            create_diagnosis(
                session,
                device_category=device_category,
                brand=brand or "Unknown",
                model=model or "Unknown",
                problem_description=problem_description,
                possible_problem=result["possible_problem"],
                confidence=float(result["confidence_score"]) / 100,
                estimated_cost=_estimated_cost_value(result["estimated_cost"]),
                repair_or_replace=result["repair_or_replace"],
                likely_component=result.get("likely_component"),
                price_confidence=result.get("price_confidence"),
                reason=result.get("repair_reason"),
                analysis_basis=result.get("analysis_basis"),
            )
        app.logger.info("Diagnosis completed")
        response = {
            "success": True,
            "mode": "demo" if demo_mode else "gemini",
            "device": {"category": device_category, "brand": brand, "model": model},
            "evidence": {
                "visible_evidence": result.get("visible_evidence", []),
                "user_reported_symptoms": result.get("user_reported_symptoms", []),
                "uncertainties": result.get("uncertainties", []),
            },
            "diagnosis": {
                "possible_problem": result["possible_problem"],
                "likely_component": result.get("likely_component", "Unknown component"),
                "possible_causes": result.get("possible_causes", []),
                "confidence_label": result["confidence"],
                "confidence_score": result["confidence_score"],
            },
            "repair": {
                "estimated_cost": result["estimated_cost"],
                "price_confidence": result.get("price_confidence", "Unavailable"),
                "estimated_repair_time": result["estimated_repair_time"],
                "repair_or_replace": result["repair_or_replace"],
                "reason": result["repair_reason"],
            },
            "price_sources": result.get("price_sources", []),
            "troubleshooting_steps": result.get("troubleshooting_steps", []),
            "safety_warning": result.get("safety_warning", ""),
            "professional_help": result.get("professional_help", ""),
            "nearby_shops": result.get("nearby_shops", []),
            "nearby_shops_message": result.get("nearby_shops_message", ""),
            "analysis_basis": result.get("analysis_basis", "description_only"),
        }
        return jsonify(response)
    except Exception:
        app.logger.exception("Diagnosis request failed")
        return jsonify(success=False, error="Unable to complete the analysis. Please try again."), 500


def _cost_range(device_category: str, problem_description: str) -> tuple[int, int]:
    ranges = {
        "Phone": (2000, 9000), "Laptop": (3000, 15000), "Refrigerator": (2500, 12000),
        "Washing Machine": (2500, 10000), "Television": (3000, 14000),
        "Air Conditioner": (3000, 16000), "Vehicle": (5000, 30000), "Other": (2000, 10000),
    }
    low, high = ranges.get(device_category, ranges["Other"])
    description = problem_description.lower()
    if any(word in description for word in ("screen", "display", "compressor", "motor")):
        return int(low * 1.3), int(high * 1.25)
    if any(word in description for word in ("software", "slow", "settings")):
        return int(low * 0.5), int(high * 0.7)
    return low, high


@app.post("/api/cost-estimate")
def api_cost_estimate():
    app.logger.info("Cost estimation request received")
    category = request.form.get("device_category", "").strip()
    brand = request.form.get("brand", "").strip()
    model = request.form.get("model", "").strip()
    problem = request.form.get("problem_description", "").strip()
    quoted_price = request.form.get("technician_quote", "").strip()
    if not category:
        return jsonify(success=False, error="Please select a device category."), 400
    if not brand:
        return jsonify(success=False, error="Please enter the brand."), 400
    if not model:
        return jsonify(success=False, error="Please enter the model."), 400
    if not problem:
        return jsonify(success=False, error="Please describe the repair problem."), 400
    try:
        quote = float(quoted_price)
    except (TypeError, ValueError):
        return jsonify(success=False, error="Please enter a valid technician quoted price."), 400
    if quote <= 0:
        return jsonify(success=False, error="Please enter a valid technician quoted price."), 400
    try:
        app.logger.info("Cost estimation validation passed")
        app.logger.info("Calculating estimate")
        low, high = _cost_range(category, problem)
        midpoint = (low + high) / 2
        if quote < low:
            assessment = "Below expected range"
            recommendation = "The technician quote appears lower than the estimated range. Confirm the parts and work included."
        elif quote > high:
            assessment = "Above expected range"
            recommendation = "The technician quote appears higher than the available estimate. Consider getting another quote."
        else:
            assessment = "Within expected range"
            recommendation = "The technician quote appears to be within the estimated range."
        app.logger.info("Cost estimation completed")
        return jsonify(
            success=True,
            technician_quote=quote,
            estimated_low=low,
            estimated_high=high,
            difference=quote - midpoint,
            assessment=assessment,
            recommendation=recommendation,
            disclaimer="Repair costs vary based on device model, parts, labor, location, and service provider.",
        )
    except Exception:
        app.logger.exception("Cost estimation request failed")
        return jsonify(success=False, error="Unable to calculate the estimate right now. Please try again."), 500


if __name__ == "__main__":
    app.run(debug=False)
