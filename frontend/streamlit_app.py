"""NiveshakAI — Home dashboard (Groww / Screener.in inspired)."""

from __future__ import annotations

import streamlit as st

import frontend.site_setup as site_setup

site_setup.ensure_project_root(__file__)

from frontend.utils.api_client import fetch_json
from frontend.utils.formatters import format_inr


st.set_page_config(
    page_title="NiveshakAI",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .hero { font-size: 2.2rem; font-weight: 700; margin-bottom: 0.2rem; }
    .sub { color: #94A3B8; margin-bottom: 1.5rem; }
    .card { background: #1E293B; padding: 1rem 1.2rem; border-radius: 12px; border: 1px solid #334155; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<p class="hero">NiveshakAI</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub">AI-powered research platform for Indian retail investors — stocks, technicals, fundamentals, news, sectors, mutual funds, portfolio & watchlist.</p>',
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns(3)
try:
    market = fetch_json("/api/market/valuation")
    col1.metric("NIFTY 50 PE", market.get("current_pe") or "N/A")
    col2.metric("Market Mood", market.get("valuation_status", "N/A"))
    col3.metric("vs Historical Avg", market.get("historical_average_pe") or "N/A")
    st.info(market.get("beginner_summary", ""))
except Exception as exc:
    st.warning(f"Market data unavailable: {exc}")

st.divider()
st.subheader("Quick Stock Lookup")
symbol = st.text_input("NSE symbol", value="RELIANCE", label_visibility="collapsed", placeholder="Try RELIANCE, TCS, INFY")
if st.button("Open Stock Research", type="primary"):
    st.session_state["symbol"] = symbol.strip().upper()
    st.switch_page("pages/1_Stock_Research.py")

try:
    summary = fetch_json(f"/api/stocks/{symbol}/summary")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Price", format_inr(summary.get("current_price")))
    c2.metric("PE", summary.get("pe_ratio") or "N/A")
    c3.metric("Sector", summary.get("sector") or "N/A")
    c4.metric("Data Source", (summary.get("data_source") or "n/a").replace("_", " "))
except Exception:
    pass

st.divider()
st.subheader("Platform Features")
features = [
    ("📊 Stock Research", "Search, charts, company profile", "pages/1_Stock_Research.py"),
    ("📉 Technical Analysis", "RSI, MACD, MA, Bollinger, trend", "pages/2_Technical_Analysis.py"),
    ("📋 Fundamentals", "Ratios, strengths, risks (screener.in style)", "pages/3_Fundamental_Analysis.py"),
    ("📰 News Sentiment", "Headlines + sentiment pulse", "pages/4_News_Sentiment.py"),
    ("🌡️ Market Valuation", "NIFTY PE & over/under-valued", "pages/5_Market_Valuation.py"),
    ("💰 Mutual Funds", "Goal-based SIP recommendations", "pages/6_Mutual_Funds.py"),
    ("🤖 AI Company Chat", "Upload annual report & ask questions", "pages/7_AI_Company_Chat.py"),
    ("🏭 Sector Analysis", "Sector momentum & ranking", "pages/8_Sector_Analysis.py"),
    ("💼 Portfolio", "Holdings, diversification, risk", "pages/9_Portfolio.py"),
    ("👁️ Watchlist", "Alerts & triggers (Tradomate style)", "pages/10_Watchlist.py"),
]

cols = st.columns(2)
for index, (title, desc, page) in enumerate(features):
    with cols[index % 2]:
        st.markdown(f"**{title}** — {desc}")
        if st.button(f"Go → {title.split(' ', 1)[1]}", key=f"nav_{index}"):
            st.switch_page(page)

st.caption("Educational project only. Not SEBI-registered advice. Inspired by Groww, Screener.in, StockEdge, StockScans & Tradomate UX patterns.")
