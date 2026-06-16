import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pandas as pd
import plotly.express as px
import streamlit as st

from frontend.utils.api_client import fetch_json

st.set_page_config(page_title="Sector Analysis", layout="wide")
st.title("🏭 Sector Analysis")
st.caption("StockScans / StockEdge-style sector momentum ranking")

period = st.selectbox("Period", ["1mo", "3mo", "6mo"], index=1)

if st.button("Rank Sectors", type="primary"):
    try:
        data = fetch_json(f"/api/sectors/analysis?period={period}")
        st.write(data.get("beginner_summary"))
        sectors = data.get("sectors", [])
        if sectors:
            frame = pd.DataFrame(sectors)
            fig = px.bar(frame, x="sector", y="average_change_percent", color="momentum_score", title="Sector performance %")
            fig.update_layout(template="plotly_dark", height=450)
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(frame[["rank", "sector", "average_change_percent", "momentum_score", "top_stock", "explanation"]], use_container_width=True)
    except Exception as exc:
        st.error(str(exc))
