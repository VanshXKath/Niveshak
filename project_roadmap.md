# Project Roadmap

This roadmap shows how we will build the platform step by step.

## Phase 1: Setup, Stock Data Engine, Basic Dashboard

Status: built in this version.

Goals:

- Create project architecture.
- Set up FastAPI backend.
- Set up Streamlit frontend.
- Fetch stock summary data.
- Fetch historical price data.
- Show a beginner-friendly dashboard.

Main learning:

- Python project structure.
- APIs.
- Dashboard basics.
- Git and GitHub basics.

## Phase 2: Technical Analysis Engine

Goals:

- Calculate RSI.
- Calculate moving averages.
- Calculate MACD.
- Add Bollinger Bands.
- Detect simple trend direction.
- Explain indicators in beginner-friendly language.

Possible files:

- `backend/app/services/technical_service.py`
- `backend/app/models/technical.py`

## Phase 3: Fundamental Analysis Engine

Goals:

- Analyze revenue, profit, debt, ROE, PE ratio, cash flow, and growth.
- Generate pros, cons, risks, and opportunities.
- Compare company valuation with sector averages when data is available.

Learning:

- Financial statements.
- Valuation.
- Business quality analysis.

## Phase 4: News Sentiment Analysis

Goals:

- Fetch stock-related news.
- Classify sentiment as positive, neutral, or negative.
- Explain possible impact.

Learning:

- NLP.
- Sentiment analysis.
- Text classification.

## Phase 5: AI Company Chatbot With RAG

Goals:

- Upload annual reports.
- Extract text from PDFs.
- Store chunks in FAISS.
- Ask questions about company documents.

Learning:

- Embeddings.
- Vector databases.
- Retrieval-Augmented Generation.

## Phase 6: Mutual Fund Recommendation Engine

Goals:

- Ask user about risk appetite, investment duration, goals, and SIP amount.
- Recommend suitable fund categories.
- Explain risk in simple language.

Learning:

- Goal-based investing.
- Risk profiling.
- Recommendation systems.

## Phase 7: Sector Analysis Dashboard

Goals:

- Track sector performance.
- Rank strongest sectors.
- Detect sector momentum.

Learning:

- Relative strength.
- Sector rotation.
- Market breadth.

## Phase 8: Optimization And Deployment

Goals:

- Add database storage.
- Move from SQLite to PostgreSQL.
- Add authentication.
- Improve caching.
- Deploy on Render or Railway.

Learning:

- Production backend systems.
- Deployment.
- Monitoring.
- Security basics.

