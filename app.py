from __future__ import annotations

import re
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from ai_engine import DEMO_MESSAGE, generate_diagnosis
from database import Diagnosis, create_diagnosis, get_diagnoses, get_session
from utils import format_currency, format_date, inject_custom_css


st.set_page_config(
    page_title="RepairLens AI",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_custom_css()

PAGES = ["Dashboard", "Diagnose Problem", "Cost Estimator", "Repair History", "About"]
DEVICE_CATEGORIES = ["Phone", "Laptop", "Refrigerator", "Washing Machine", "Television", "Air Conditioner", "Vehicle", "Other"]


def render_sidebar() -> str:
    with st.sidebar:
        st.markdown(
            '<div class="brand"><div class="brand-mark">✦</div>'
            '<div><div class="brand-name">RepairLens <span>AI</span></div>'
            '<div class="brand-caption">Repair decision assistant</div></div></div>',
            unsafe_allow_html=True,
        )
        st.divider()
        return st.radio("Workspace", PAGES, label_visibility="collapsed")


def metric_card(label: str, value: str, icon: str, tone: str) -> None:
    st.markdown(
        f'<div class="metric-card"><div class="metric-icon {tone}">{icon}</div>'
        f'<div><div class="metric-label">{label}</div><div class="metric-value">{value}</div></div></div>',
        unsafe_allow_html=True,
    )


def get_dashboard_metrics(diagnoses: list[Diagnosis]) -> tuple[int, int, int, float]:
    total = len(diagnoses)
    repairs = sum(item.repair_or_replace.lower().startswith("repair") for item in diagnoses)
    replacements = sum(item.repair_or_replace.lower().startswith(("replace", "professional")) for item in diagnoses)
    costs = [item.estimated_cost for item in diagnoses if item.estimated_cost is not None]
    return total, repairs, replacements, sum(costs) / len(costs) if costs else 0.0


def _diagnosis_frame(diagnoses: list[Diagnosis]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Date": format_date(item.date),
                "Device": f"{item.brand or 'Unknown'} {item.model or 'Unknown'}",
                "Category": item.device_category,
                "Brand": item.brand or "Unknown",
                "Model": item.model or "Unknown",
                "Problem": item.problem_description,
                "Possible Problem": item.possible_problem or "Assessment pending",
                "Confidence": f"{item.confidence:.0%}",
                "Estimated Cost": format_currency(item.estimated_cost),
                "Estimated Cost Value": item.estimated_cost or 0,
                "Recommendation": item.repair_or_replace or "Review",
                "_id": item.id,
            }
            for item in diagnoses
        ]
    )


def render_dashboard(diagnoses: list[Diagnosis]) -> None:
    st.markdown(
        '<div class="hero"><div class="hero-copy"><div class="eyebrow">SMARTER DEVICE CARE</div>'
        '<h1>RepairLens <span>AI</span></h1><p class="hero-subtitle">AI-Powered Repair Decision Assistant</p>'
        '<p class="hero-description">Understand what may be wrong with your device, estimate repair costs, '
        'and make confident repair-or-replace decisions with practical, safe guidance.</p></div>'
        '<div class="hero-art"><div class="orbit orbit-one"></div><div class="orbit orbit-two"></div>'
        '<div class="hero-device">🔧</div></div></div>',
        unsafe_allow_html=True,
    )
    if st.button("Start Diagnosis  →", type="primary"):
        st.session_state["page"] = "Diagnose Problem"
        st.rerun()

    st.markdown('<div class="section-heading"><h2>Overview</h2><span>Live insights from your repair activity</span></div>', unsafe_allow_html=True)
    total, repairs, replacements, average = get_dashboard_metrics(diagnoses)
    columns = st.columns(4)
    for column, card in zip(
        columns,
        [
            ("Total Diagnoses", str(total), "⌁", "blue"),
            ("Repairs Recommended", str(repairs), "✓", "green"),
            ("Replacement Recommended", str(replacements), "↻", "purple"),
            ("Average Estimated Cost", format_currency(average), "₹", "orange"),
        ],
    ):
        with column:
            metric_card(*card)

    if diagnoses:
        render_dashboard_charts(diagnoses)
    st.markdown('<div class="section-heading recent-heading"><h2>Recent Diagnoses</h2><span>Latest device assessments</span></div>', unsafe_allow_html=True)
    if not diagnoses:
        st.markdown(
            '<div class="empty-state"><div class="empty-icon">✦</div><h3>No diagnoses yet</h3>'
            '<p>Your recent assessments will appear here. Start a diagnosis to see your repair insights.</p></div>',
            unsafe_allow_html=True,
        )
        return
    for diagnosis in diagnoses[:5]:
        recommendation = diagnosis.repair_or_replace or "Review"
        recommendation_class = "recommend-repair" if recommendation.lower().startswith("repair") else "recommend-replace"
        st.markdown(
            f'<div class="diagnosis-row"><div class="device-avatar">▣</div><div class="diagnosis-main">'
            f'<strong>{diagnosis.brand or "Unknown"} {diagnosis.model or diagnosis.device_category}</strong>'
            f'<span>{diagnosis.problem_description[:85]} · {format_date(diagnosis.date)}</span>'
            f'<small>{diagnosis.possible_problem or "Assessment pending"}</small></div>'
            f'<span class="recommendation {recommendation_class}">{recommendation}</span>'
            f'<strong class="row-cost">{format_currency(diagnosis.estimated_cost)}</strong></div>',
            unsafe_allow_html=True,
        )


def render_dashboard_charts(diagnoses: list[Diagnosis]) -> None:
    frame = _diagnosis_frame(diagnoses)
    if len(frame) < 2:
        return
    st.markdown('<div class="section-heading"><h2>Analytics</h2><span>Patterns across saved assessments</span></div>', unsafe_allow_html=True)
    chart_columns = st.columns(3)
    with chart_columns[0]:
        recommendation_counts = frame["Recommendation"].str.extract(r"^(Repair|Replace|Professional)", expand=False).fillna("Review").value_counts()
        figure, axis = plt.subplots(figsize=(4, 3))
        axis.bar(recommendation_counts.index, recommendation_counts.values, color=["#3857e8", "#8b5cf6", "#f2994a"][: len(recommendation_counts)])
        axis.set_title("Repair vs Replacement", fontsize=12, pad=12)
        axis.set_ylabel("Diagnoses")
        axis.spines[["top", "right"]].set_visible(False)
        st.pyplot(figure, use_container_width=True)
        plt.close(figure)
    with chart_columns[1]:
        category_counts = frame["Category"].value_counts()
        figure, axis = plt.subplots(figsize=(4, 3))
        axis.barh(category_counts.index, category_counts.values, color="#5d72e8")
        axis.set_title("Diagnoses by Device Category", fontsize=12, pad=12)
        axis.spines[["top", "right", "left"]].set_visible(False)
        st.pyplot(figure, use_container_width=True)
        plt.close(figure)
    with chart_columns[2]:
        figure, axis = plt.subplots(figsize=(4, 3))
        axis.hist(frame["Estimated Cost Value"], bins=min(5, len(frame)), color="#ee923c", edgecolor="white")
        axis.set_title("Estimated Repair Cost Overview", fontsize=12, pad=12)
        axis.set_xlabel("Estimated average (₹)")
        axis.set_ylabel("Diagnoses")
        axis.spines[["top", "right"]].set_visible(False)
        st.pyplot(figure, use_container_width=True)
        plt.close(figure)


def render_diagnose() -> None:
    st.title("Diagnose Problem")
    st.caption("Combine your device details, symptoms, and an optional image for a cautious repair assessment.")
    with st.form("diagnosis_form"):
        left, right = st.columns(2)
        with left:
            category = st.selectbox("Device category", DEVICE_CATEGORIES)
            brand = st.text_input("Brand", placeholder="e.g. Apple, Samsung, Dell")
            model = st.text_input("Model", placeholder="e.g. iPhone 14, Inspiron 15")
        with right:
            image = st.file_uploader("Device image (optional)", type=["jpg", "jpeg", "png", "webp"])
            problem = st.text_area("Problem description", placeholder="Describe symptoms, sounds, damage, or error messages...", height=145)
        submitted = st.form_submit_button("Analyze Problem with AI  →", type="primary")
    if image:
        try:
            st.image(image, caption="Uploaded device image", width=360)
        except Exception:
            st.error("This image could not be previewed. Please upload a valid JPG, JPEG, PNG, or WEBP file.")
            image = None
    if submitted:
        if not problem.strip():
            st.error("Please describe the problem before running a diagnosis.")
            return
        with st.spinner("Analyzing your device..."):
            result, demo_mode = generate_diagnosis(
                category, brand.strip(), model.strip(), problem.strip(),
                image.getvalue() if image else None,
                image.type if image else None,
            )
        st.warning(DEMO_MESSAGE) if demo_mode else st.success("Gemini assessment complete. Review these estimates below.")
        try:
            with get_session() as session:
                create_diagnosis(
                    session,
                    date=datetime.now(),
                    device_category=category,
                    brand=brand.strip() or "Unknown",
                    model=model.strip() or "Unknown",
                    problem_description=problem.strip(),
                    possible_problem=result["possible_problem"],
                    confidence=float(result["confidence_score"]) / 100,
                    estimated_cost=_cost_value(result["estimated_cost"]),
                    repair_or_replace=result["repair_or_replace"],
                )
        except Exception:
            st.error("The assessment was generated, but it could not be saved to repair history.")
        _render_diagnosis_result(result)


def _cost_value(cost_text: str) -> float:
    values = [float(value.replace(",", "")) for value in re.findall(r"[\d,]+", str(cost_text))]
    return sum(values) / len(values) if values else 0.0


def _render_diagnosis_result(result: dict[str, object]) -> None:
    st.markdown('<div class="ai-disclaimer">AI results are estimates and possible causes, not a guaranteed technical diagnosis.</div>', unsafe_allow_html=True)
    columns = st.columns(2)
    with columns[0]:
        st.markdown(f"### 🔍 Possible Problem\n{result['possible_problem']}")
        st.markdown("### 🧩 Possible Causes")
        for cause in result["possible_causes"]:
            st.markdown(f"- {cause}")
        st.markdown(f"### 🎯 AI Confidence\n**{result['confidence_score']}%** · {result['confidence']}")
        st.markdown(f"### 💰 Estimated Repair Cost\n**{result['estimated_cost']}**")
    with columns[1]:
        st.markdown(f"### ⏱ Estimated Repair Time\n{result['estimated_repair_time']}")
        st.markdown(f"### 🔧 Repair vs Replacement\n**{result['repair_or_replace']}**")
        st.markdown(f"**Why this recommendation?** {result['repair_reason']}")
        st.markdown("### 🛠 Safe Troubleshooting")
        for step in result["troubleshooting_steps"]:
            st.markdown(f"- {step}")
    st.warning(f"⚠️ **Safety Warning**  \n{result['safety_warning']}")
    st.info(f"👨‍🔧 **Professional Help**  \n{result['professional_help']}")


def _estimate_range(category: str, problem: str) -> tuple[int, int]:
    base_ranges = {
        "Phone": (2000, 9000), "Laptop": (3000, 15000), "Refrigerator": (2500, 12000),
        "Washing Machine": (2500, 10000), "Television": (3000, 14000),
        "Air Conditioner": (3000, 16000), "Vehicle": (5000, 30000), "Other": (2000, 10000),
    }
    low, high = base_ranges[category]
    text = problem.lower()
    if any(word in text for word in ("screen", "display", "compressor", "motor")):
        low, high = int(low * 1.3), int(high * 1.25)
    elif any(word in text for word in ("software", "slow", "settings")):
        low, high = int(low * 0.5), int(high * 0.7)
    return low, high


def render_cost_estimator() -> None:
    st.title("Cost Estimator")
    st.caption("Compare a technician quote with a broad, device-aware estimate.")
    with st.form("cost_estimator_form"):
        left, right = st.columns(2)
        with left:
            category = st.selectbox("Device category", DEVICE_CATEGORIES, key="estimate_category")
            brand = st.text_input("Brand", key="estimate_brand")
            model = st.text_input("Model", key="estimate_model")
        with right:
            problem = st.text_area("Problem description", key="estimate_problem", height=120)
            quote = st.number_input("Technician quoted price (₹)", min_value=0.0, step=500.0, format="%.0f")
        submitted = st.form_submit_button("Evaluate Quote  →", type="primary")
    if not submitted:
        return
    if not problem.strip():
        st.error("Please describe the problem to estimate a relevant range.")
        return
    low, high = _estimate_range(category, problem)
    if quote <= 0:
        st.error("Please enter a technician quote greater than ₹0.")
        return
    difference = quote - ((low + high) / 2)
    if low <= quote <= high:
        evaluation, tone = "Within Expected Range", "success"
    elif quote > high:
        evaluation, tone = "Higher Than Expected", "warning"
    else:
        evaluation, tone = "Lower Than Expected", "info"
    st.markdown('<div class="estimate-card">', unsafe_allow_html=True)
    results = st.columns(4)
    for column, label, value in zip(
        results,
        ["Estimated Repair Cost Range", "Technician Quote", "Difference from Midpoint", "Quote Evaluation"],
        [f"{format_currency(low)} – {format_currency(high)}", format_currency(quote), f"{'+' if difference >= 0 else ''}{format_currency(difference)}", evaluation],
    ):
        with column:
            st.metric(label, value)
    st.markdown("</div>", unsafe_allow_html=True)
    getattr(st, tone)(f"**{evaluation}** — Compare the scope of work, parts, warranty, and service quality before deciding.")
    st.caption("Repair costs are estimates only. Actual prices may vary depending on device model, location, replacement parts, technician and service center.")


def render_history() -> None:
    st.title("Repair History")
    st.caption("Review saved assessments and the decisions made for each device.")
    diagnoses = get_diagnoses()
    if not diagnoses:
        st.info("No diagnosis history yet.")
        return
    frame = _diagnosis_frame(diagnoses)
    st.dataframe(
        frame[["Date", "Device", "Brand", "Model", "Problem", "Possible Problem", "Confidence", "Estimated Cost", "Recommendation"]],
        use_container_width=True,
        hide_index=True,
    )
    selected_id = st.selectbox(
        "View complete diagnosis",
        options=[item.id for item in diagnoses],
        format_func=lambda item_id: next((f"{item.brand} {item.model} · {format_date(item.date)}" for item in diagnoses if item.id == item_id), str(item_id)),
    )
    selected = next(item for item in diagnoses if item.id == selected_id)
    st.markdown('<div class="detail-card">', unsafe_allow_html=True)
    st.markdown(f"### {selected.brand} {selected.model}")
    st.write(f"**Date:** {format_date(selected.date)}  ·  **Category:** {selected.device_category}")
    st.write(f"**Problem:** {selected.problem_description}")
    st.write(f"**Possible problem:** {selected.possible_problem}")
    st.write(f"**Confidence:** {selected.confidence:.0%}  ·  **Estimated cost:** {format_currency(selected.estimated_cost)}")
    st.write(f"**Recommendation:** {selected.repair_or_replace}")
    st.markdown("</div>", unsafe_allow_html=True)


def render_about() -> None:
    st.title("About RepairLens AI")
    st.caption("A practical decision-support assistant for everyday device repair questions.")
    st.markdown("## PROJECT OVERVIEW")
    st.write("RepairLens AI is an AI-powered repair decision assistant designed to help users understand possible problems with damaged or malfunctioning devices.")
    st.markdown("## REAL-WORLD PROBLEM")
    st.write("Users often do not know what may be wrong with a device, whether repair or replacement is better, how to understand technician quotes, or which troubleshooting steps are safe.")
    st.markdown("## OUR SOLUTION")
    st.write("Users provide device information, a problem description, and an optional image. RepairLens AI returns possible causes, confidence, estimated cost and time, a repair-vs-replacement recommendation, safe guidance, and safety warnings.")
    st.markdown("## WORKFLOW")
    st.markdown('<div class="workflow">User Input &nbsp; → &nbsp; Image + Problem Description &nbsp; → &nbsp; AI Analysis &nbsp; → &nbsp; Possible Causes &nbsp; → &nbsp; Confidence &nbsp; → &nbsp; Cost Estimate &nbsp; → &nbsp; Repair vs Replacement &nbsp; → &nbsp; Safe Guidance</div>', unsafe_allow_html=True)
    st.markdown("## TECHNOLOGY STACK")
    st.write("Python · Streamlit · Google Gemini · SQLAlchemy · SQLite · Pandas · NumPy · Scikit-learn · Matplotlib · Seaborn · LangChain")
    st.markdown("## LIMITATIONS")
    st.write("AI results are estimates and cannot guarantee a technical diagnosis. Images cannot reveal every internal fault, repair costs vary by location and device, and professional inspection may be required.")


def main() -> None:
    selected = render_sidebar()
    page = st.session_state.pop("page", selected)
    try:
        diagnoses = get_diagnoses()
    except Exception:
        diagnoses = []
        st.error("Diagnosis history is temporarily unavailable. You can still use the other pages.")
    if page == "Dashboard":
        render_dashboard(diagnoses)
    elif page == "Diagnose Problem":
        render_diagnose()
    elif page == "Repair History":
        render_history()
    elif page == "Cost Estimator":
        render_cost_estimator()
    else:
        render_about()


if __name__ == "__main__":
    main()
