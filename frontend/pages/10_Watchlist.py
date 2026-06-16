import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st

from frontend.utils.api_client import fetch_json, post_json

st.set_page_config(page_title="Watchlist", layout="wide")
st.title("👁️ Watchlist Intelligence")
st.caption("Tradomate-style alerts: price & RSI triggers")

c1, c2 = st.columns(2)
with c1:
    with st.form("watchlist_add"):
        symbol = st.text_input("Add symbol", value="INFY")
        notes = st.text_input("Notes", value="Watch for breakout")
        if st.form_submit_button("Add to watchlist"):
            try:
                post_json("/api/watchlist/items", {"symbol": symbol, "notes": notes})
                st.success("Added")
            except Exception as exc:
                st.error(str(exc))

with c2:
    with st.form("alert_add"):
        alert_symbol = st.text_input("Alert symbol", value="RELIANCE")
        alert_type = st.selectbox("Type", ["price_above", "price_below", "rsi_above", "rsi_below"])
        threshold = st.number_input("Threshold", value=2500.0)
        if st.form_submit_button("Create alert"):
            try:
                post_json(
                    "/api/watchlist/alerts",
                    {"symbol": alert_symbol, "alert_type": alert_type, "threshold": threshold},
                )
                st.success("Alert created")
            except Exception as exc:
                st.error(str(exc))

if st.button("Refresh Intelligence", type="primary"):
    try:
        data = fetch_json("/api/watchlist/intelligence")
        st.write(data.get("beginner_summary"))
        st.metric("Triggered alerts", data.get("triggered_count", 0))

        st.subheader("Watchlist")
        for item in data.get("watchlist", []):
            st.write(f"**{item['symbol']}** — {item.get('notes') or 'No notes'}")

        st.subheader("Alerts")
        for alert in data.get("alerts", []):
            status = "🔔 TRIGGERED" if alert.get("triggered") else "⏳ Waiting"
            st.write(f"{status} | {alert['symbol']} | {alert['alert_type']} @ {alert.get('threshold')}")
            if alert.get("trigger_detail"):
                st.caption(alert["trigger_detail"])
    except Exception as exc:
        st.error(str(exc))
