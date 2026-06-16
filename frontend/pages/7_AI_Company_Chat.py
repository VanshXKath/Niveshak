import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st

from frontend.utils.api_client import post_json, upload_pdf

st.set_page_config(page_title="AI Company Chat", layout="wide")
st.title("🤖 AI Company Chat")
st.caption("Upload annual report PDF → RAG Q&A (FAISS + optional Gemini)")

symbol = st.text_input("NSE Symbol", value=st.session_state.get("symbol", "RELIANCE")).strip().upper()
uploaded = st.file_uploader("Upload annual report / investor presentation (PDF)", type=["pdf"])

if uploaded and st.button("Index Document"):
    try:
        result = upload_pdf("/api/chat/upload", symbol, uploaded.read(), uploaded.name)
        st.success(result.get("message"))
        st.write(f"Chunks indexed: {result.get('chunks_indexed')}")
    except Exception as exc:
        st.error(str(exc))

question = st.text_input("Ask a question", placeholder="What were the main revenue drivers last year?")
if st.button("Ask AI", type="primary") and question:
    try:
        answer = post_json("/api/chat/ask", {"symbol": symbol, "question": question})
        st.session_state["symbol"] = symbol
        st.subheader("Answer")
        st.write(answer.get("answer"))
        if answer.get("used_ai"):
            st.caption("Powered by Gemini")
        else:
            st.caption("RAG keyword mode — add GEMINI_API_KEY for richer answers")
        if answer.get("sources"):
            with st.expander("Sources"):
                for source in answer["sources"]:
                    st.write(source)
    except Exception as exc:
        st.error(str(exc))
