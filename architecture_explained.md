# Architecture Explained

Architecture means how the project is arranged.

Good architecture is like a well-organized kitchen. You know where the ingredients are, where cooking happens, and where food is served.

## Big Picture

```text
User
  |
  v
Streamlit Frontend
  |
  v
FastAPI Backend
  |
  v
yfinance
  |
  v
Yahoo Finance market data
```

## Why We Use FastAPI

FastAPI helps us create an API.

An API is a messenger. The frontend says:

> Give me RELIANCE stock data.

The backend replies:

> Here is price, volume, PE ratio, market cap, and chart data.

FastAPI is good because it is:

- fast,
- beginner-friendly after the basics,
- used in professional Python backend systems,
- automatically gives API docs at `/docs`.

## Why We Use Streamlit

Streamlit helps us build dashboards quickly with Python.

For Phase 1, it lets us create:

- a search box,
- metrics,
- charts,
- simple explanations.

Later, if we want a more advanced frontend, we can move to React. For now, Streamlit is perfect for learning and fast product building.

## Why We Use yfinance

`yfinance` is a Python library that fetches market data from Yahoo Finance.

For Indian NSE stocks, Yahoo Finance symbols usually end with `.NS`.

Examples:

- `RELIANCE` becomes `RELIANCE.NS`
- `TCS` becomes `TCS.NS`
- `INFY` becomes `INFY.NS`

The backend handles this automatically in `StockService.normalize_symbol`.

## File-By-File Explanation

### `backend/app/main.py`

This is the backend entry point.

It creates the FastAPI app, enables CORS, defines a health check route, and connects stock API routes.

CORS allows Streamlit and FastAPI to talk even though they run on different ports.

### `backend/app/api/routes/stocks.py`

This file defines stock API URLs.

It currently has:

- `/api/stocks/{symbol}/summary`
- `/api/stocks/{symbol}/history`

Routes should stay small. They receive requests and call service classes.

### `backend/app/services/stock_service.py`

This is where stock data work happens.

It:

- cleans stock symbols,
- calls `yfinance`,
- extracts useful fields,
- handles missing values,
- creates beginner-friendly summaries.

Later, technical analysis and fundamental analysis engines will be separate services.

### `backend/app/models/stock.py`

This file defines response shapes using Pydantic.

Pydantic is like a strict form. It makes sure the API returns predictable data.

For example, stock history must look like:

```text
date, open, high, low, close, volume
```

### `backend/app/core/config.py`

This file stores settings.

Today it reads:

- app name,
- backend host,
- backend port.

Later it can read database URLs, API keys, and AI model settings.

### `frontend/streamlit_app.py`

This is the dashboard.

It:

- shows a search box,
- calls the backend using `requests`,
- displays metrics,
- draws a candlestick chart with Plotly,
- shows beginner explanations.

## Data Flow

When a user searches `TCS`:

1. Streamlit reads the text box.
2. Streamlit calls `/api/stocks/TCS/summary`.
3. FastAPI receives the request.
4. `stocks.py` calls `StockService`.
5. `StockService` converts `TCS` to `TCS.NS`.
6. `yfinance` fetches market data.
7. FastAPI returns clean JSON.
8. Streamlit displays it.

## How To Modify Later

To add a new backend feature:

1. Create or update a service in `backend/app/services`.
2. Add a response model in `backend/app/models`.
3. Add a route in `backend/app/api/routes`.
4. Display it in `frontend/streamlit_app.py`.

Example future feature:

- Create `technical_service.py`.
- Add RSI and moving average calculations.
- Add `/api/stocks/{symbol}/technical`.
- Show the result in Streamlit.
