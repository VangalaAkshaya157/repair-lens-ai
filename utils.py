from __future__ import annotations

from datetime import datetime

import streamlit as st


def format_currency(value: float | None) -> str:
    return "₹0" if not value else f"₹{value:,.0f}"


def format_date(value: datetime | None) -> str:
    return value.strftime("%d %b %Y") if value else "Recently"


def inject_custom_css() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
        :root { --ink:#182230; --muted:#718096; --line:#e8edf4; --blue:#3857e8; }
        .stApp { background:#f7f9fc; color:var(--ink); font-family:'DM Sans',sans-serif; }
        [data-testid="stSidebar"] { background:#fff; border-right:1px solid var(--line); }
        [data-testid="stSidebar"] > div:first-child { padding:28px 20px; }
        .brand { display:flex; gap:11px; align-items:center; }
        .brand-mark { width:37px; height:37px; border-radius:11px; background:linear-gradient(135deg,#405bf0,#7f5bf0); color:white; display:grid; place-items:center; font-size:21px; }
        .brand-name { font:700 17px 'Space Grotesk'; color:#1b2533; }.brand-name span,.hero h1 span { color:var(--blue); }
        .brand-caption { color:#96a0b1; font-size:10px; margin-top:2px; }
        [data-testid="stRadio"] label { border-radius:9px; padding:7px 10px; color:#687386; font-weight:500; }
        [data-testid="stRadio"] label:hover { background:#f2f5ff; color:var(--blue); }
        .block-container { max-width:1240px; padding:42px 5% 70px; }
        .hero { display:flex; justify-content:space-between; min-height:250px; padding:42px 48px; border-radius:22px; background:linear-gradient(120deg,#eef2ff,#f7f5ff); overflow:hidden; position:relative; }
        .eyebrow { color:var(--blue); font-size:11px; font-weight:700; letter-spacing:1.7px; margin-bottom:14px; }
        .hero h1 { font:700 42px 'Space Grotesk'; letter-spacing:-1.5px; margin:0; color:#1a2433; }.hero-subtitle { font:600 18px 'Space Grotesk'; margin:7px 0 13px; color:#46536b; }.hero-description { color:#68758b; max-width:570px; line-height:1.6; margin:0; }
        .hero-art { width:200px; position:relative; }.hero-device { position:absolute; inset:48px 45px; display:grid; place-items:center; width:100px; height:100px; border-radius:30px; background:white; box-shadow:0 20px 50px #7d8ee044; font-size:43px; transform:rotate(-12deg); }.orbit { border:1px solid #cbd4ff; border-radius:50%; position:absolute; }.orbit-one { width:190px; height:190px; top:0; left:0; }.orbit-two { width:145px; height:145px; top:24px; left:23px; border-style:dashed; }
        .stButton button[kind="primary"] { background:var(--blue); border:0; border-radius:10px; padding:10px 19px; font-weight:700; box-shadow:0 7px 18px #3857e833; }
        .section-heading { display:flex; align-items:baseline; gap:13px; margin:36px 0 16px; }.section-heading h2 { font:600 21px 'Space Grotesk'; margin:0; }.section-heading span { color:#9aa5b6; font-size:13px; }
        .metric-card { background:white; border:1px solid var(--line); border-radius:15px; padding:20px 16px; display:flex; gap:13px; align-items:center; min-height:78px; box-shadow:0 5px 15px #20305005; }.metric-icon { width:38px; height:38px; border-radius:11px; display:grid; place-items:center; font-weight:700; font-size:18px; }.metric-icon.blue { background:#edf1ff; color:#405be9; }.metric-icon.green { background:#e8f8f1; color:#18a56d; }.metric-icon.purple { background:#f1ebff; color:#8b5cf6; }.metric-icon.orange { background:#fff1e5; color:#ee923c; }.metric-label { color:#8994a7; font-size:12px; }.metric-value { font:700 22px 'Space Grotesk'; margin-top:4px; }
        .empty-state { text-align:center; background:white; border:1px dashed #d8dfeb; border-radius:16px; padding:45px 20px; }.empty-icon { margin:auto; width:42px; height:42px; display:grid; place-items:center; border-radius:13px; background:#eef2ff; color:var(--blue); font-size:23px; }.empty-state h3 { margin:13px 0 5px; font:600 17px 'Space Grotesk'; }.empty-state p { color:#8a96a9; margin:0; font-size:13px; }
        .diagnosis-row { display:flex; align-items:center; gap:14px; padding:16px 18px; margin-bottom:9px; background:white; border:1px solid var(--line); border-radius:13px; }.device-avatar { width:38px; height:38px; border-radius:11px; display:grid; place-items:center; background:#eef2ff; color:var(--blue); }.diagnosis-main { flex:1; display:flex; flex-direction:column; gap:3px; }.diagnosis-main strong { font-size:14px; }.diagnosis-main span { color:#8994a7; font-size:12px; }.recommendation { font-size:11px; font-weight:700; padding:6px 10px; border-radius:20px; }.recommend-repair { background:#e8f8f1; color:#159966; }.recommend-replace { background:#fff0e9; color:#d8753d; }.row-cost { min-width:75px; text-align:right; font-size:14px; }
        .ai-disclaimer { background:#fff8e8; border:1px solid #f3dfac; color:#876820; border-radius:10px; padding:12px 15px; margin:20px 0; font-size:13px; }
        .estimate-card, .detail-card { background:white; border:1px solid var(--line); border-radius:16px; padding:22px; margin:18px 0; box-shadow:0 5px 15px #20305005; }
        .workflow { background:linear-gradient(100deg,#eef2ff,#f7f5ff); border:1px solid #dce3ff; border-radius:14px; padding:19px; color:#405be9; font-weight:600; line-height:2; }
        [data-testid="stDataFrame"] { border:1px solid var(--line); border-radius:12px; overflow:hidden; }
        [data-testid="stMetric"] { min-height:80px; }
        @media (max-width:700px) { .hero { padding:28px; }.hero-art { display:none; }.hero h1 { font-size:34px; }.block-container { padding:28px 5%; } }
        </style>
        """,
        unsafe_allow_html=True,
    )
