import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st

from frontend.utils.api_client import post_json

st.set_page_config(page_title="Mutual Funds", layout="wide")
st.title("💰 Mutual Fund Recommendations")
st.caption("Groww-style goal planner — educational categories only")

goal = st.selectbox("Goal", ["wealth_creation", "tax_saving", "emergency_fund"])
risk = st.selectbox("Risk appetite", ["low", "moderate", "high"])
horizon = st.slider("Investment horizon (years)", 1, 30, 7)
sip = st.number_input("Monthly SIP (INR)", min_value=500.0, value=5000.0, step=500.0)

if st.button("Get Recommendations", type="primary"):
    try:
        data = post_json(
            "/api/mutual-funds/recommend",
            {
                "goal": goal,
                "risk_appetite": risk,
                "investment_horizon_years": horizon,
                "monthly_sip": sip,
            },
        )
        st.write(data.get("profile_summary"))
        st.write(data.get("beginner_summary"))
        for rec in data.get("recommendations", []):
            with st.expander(rec["category"]):
                st.write(f"Risk: {rec['risk']} | Horizon: {rec['horizon_years']}")
                st.write(rec["why"])
                st.write("Example funds:", ", ".join(rec.get("example_funds", [])))
                st.metric("Suggested SIP", f"₹{rec.get('suggested_sip', 0):,.0f}")
    except Exception as exc:
        st.error(str(exc))
