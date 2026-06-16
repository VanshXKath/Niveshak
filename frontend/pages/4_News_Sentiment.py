import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st

from frontend.utils.api_client import fetch_json
from frontend.utils.formatters import sentiment_color

st.set_page_config(page_title="News Sentiment", layout="wide")
st.title("📰 News Sentiment")
st.caption("Groww-style news pulse with keyword sentiment scoring")

symbol = st.text_input("NSE Symbol", value=st.session_state.get("symbol", "RELIANCE")).strip().upper()

if st.button("Scan News", type="primary"):
    try:
        data = fetch_json(f"/api/news/{symbol}")
        st.session_state["symbol"] = symbol
        st.metric("Overall Sentiment", f"{sentiment_color(data['overall_sentiment'])} {data['overall_sentiment'].title()}")
        st.write(data.get("summary"))

        for article in data.get("articles", []):
            with st.expander(f"{sentiment_color(article['sentiment'])} {article['title']}"):
                st.write(f"Source: {article.get('source') or 'N/A'} | {article.get('published') or ''}")
                st.write(f"Sentiment: **{article['sentiment']}** ({article['sentiment_score']})")
                st.write(article.get("impact"))
                if article.get("link"):
                    st.link_button("Read", article["link"])
    except Exception as exc:
        st.error(str(exc))
