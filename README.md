# Indian Stock Market AI Screener

This project is a beginner-friendly AI-powered stock market analysis platform for Indian retail investors.

Phase 1 builds the foundation:

- A FastAPI backend that fetches stock data.
- A Streamlit dashboard where users search NSE stocks.
- Basic company metrics and price charts.
- Documentation that explains the project like you are new to coding.

This is not financial advice. It is an educational software project that helps beginners understand market data.

## What We Are Building

Think of the project like a restaurant.

- The backend is the kitchen. It fetches raw ingredients, cleans them, and prepares useful data.
- The frontend is the dining table. It shows the prepared information in a simple way.
- The stock data API is the market supplier. In Phase 1 we use `yfinance`.

When you search `RELIANCE`, the app converts it to `RELIANCE.NS`, asks Yahoo Finance for data, and displays price, PE ratio, volume, market cap, and a chart.

## Folder Structure

```text
Screener/
+-- backend/
|   +-- app/
|       +-- api/routes/stocks.py
|       +-- core/config.py
|       +-- main.py
|       +-- models/stock.py
|       +-- services/stock_service.py
+-- frontend/
|   +-- streamlit_app.py
+-- .env.example
+-- .gitignore
+-- requirements.txt
+-- README.md
+-- beginner_setup_guide.md
+-- architecture_explained.md
+-- project_roadmap.md
```

## Quick Start

Open PowerShell inside this folder:

```powershell
cd C:\Users\vansh\OneDrive\Documents\Screener
```

Create a virtual environment:

```powershell
py -3 -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install libraries:

```powershell
python -m pip install -r requirements.txt
```

Start the backend:

```powershell
uvicorn backend.app.main:app --reload
```

Open a second PowerShell window, activate the same virtual environment, then start Streamlit:

```powershell
.\.venv\Scripts\Activate.ps1
streamlit run frontend/streamlit_app.py
```

If `uvicorn` or `streamlit` is not recognized, use:

```powershell
python -m uvicorn backend.app.main:app --reload
python -m streamlit run frontend/streamlit_app.py
```

The dashboard will open in your browser.

## Useful URLs

- Backend health check: `http://127.0.0.1:8000`
- Backend API docs: `http://127.0.0.1:8000/docs`
- Streamlit dashboard: usually `http://localhost:8501`

## Example Stocks To Try

- `RELIANCE`
- `TCS`
- `INFY`
- `HDFCBANK`
- `SBIN`

## GitHub Setup

Git remembers your project history. GitHub stores it online.

First check Git:

```powershell
git status
```

Add files:

```powershell
git add .
```

Create your first commit:

```powershell
git commit -m "Build phase 1 stock data dashboard"
```

Create a new GitHub repository on github.com, then connect this local folder:

```powershell
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` and `YOUR_REPOSITORY_NAME` with your real GitHub details.

## What To Learn From Phase 1

- Python functions and classes.
- APIs using FastAPI.
- UI dashboards using Streamlit.
- Stock symbols and basic market data.
- Project folders and clean architecture.
- Git and GitHub basics.
