# Beginner Setup Guide

This guide assumes you are new to coding.

## 1. What Is A Project Folder?

A project folder is like a school bag for one subject. Everything related to this stock screener lives inside:

```text
E:\stock_screener_phase1_with_guides
```

Keep code, documentation, and settings together so the project stays organized.

You can also run the automated setup script:

```powershell
.\scripts\setup.ps1
```

## 2. What Is Python?

Python is the programming language we use for the backend and dashboard.

In this project, Python:

- fetches stock data,
- processes numbers,
- runs the API,
- runs the Streamlit dashboard,
- later runs AI/ML models.

Check Python:

```powershell
py -3 --version
```

If Python is installed, you will see a version number.

## 3. What Is A Virtual Environment?

A virtual environment is a private toolbox for this project.

Without it, every Python project on your computer shares the same tools. That becomes messy. With `.venv`, this project gets its own copy of libraries.

Create it:

```powershell
py -3 -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

When activated, your terminal usually shows `(.venv)`.

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try activation again.

## 4. What Is requirements.txt?

`requirements.txt` is the shopping list of Python libraries.

This project uses:

- `fastapi`: creates the backend API.
- `uvicorn`: runs the FastAPI server.
- `streamlit`: creates the dashboard.
- `yfinance`: fetches stock market data.
- `pandas`: works with tables of data.
- `plotly`: creates interactive charts.
- `requests`: lets Streamlit call the backend.
- `python-dotenv`: loads settings from `.env`.
- `pydantic`: validates API response data.
- `pytest`: runs automated tests.
- `httpx`: used by FastAPI test client.

Install everything:

```powershell
python -m pip install -r requirements.txt
```

## 5. How To Run The Backend

The backend is the data engine.

Run:

```powershell
python -m uvicorn backend.app.main:app --reload
```

Meaning:

- `uvicorn`: starts the server.
- `backend.app.main`: file path to `main.py`.
- `app`: the FastAPI app object inside `main.py`.
- `--reload`: restart automatically when code changes.

Visit:

```text
http://127.0.0.1:8000/docs
```

That page lets you test API endpoints in the browser.

## 6. How To Run The Frontend

Open another PowerShell window in the same folder.

Activate the virtual environment again:

```powershell
.\.venv\Scripts\Activate.ps1
```

Run:

```powershell
python -m streamlit run frontend/streamlit_app.py
```

Streamlit will open the dashboard in your browser.

## 7. Common Errors

### Error: command not found

It means your computer cannot find that command. Check Python installation and virtual environment activation.

### Error: cannot reach backend

Start the backend first:

```powershell
python -m uvicorn backend.app.main:app --reload
```

Then run Streamlit.

### Error: no stock data found

Try a valid NSE symbol:

- `RELIANCE`
- `TCS`
- `INFY`
- `SBIN`

The app automatically adds `.NS` for NSE stocks.

## 8. How To Stop Servers

Press:

```text
Ctrl + C
```

Do this in each terminal where a server is running.

## 9. How To Test

Tests check that your code works without needing live market data.

```powershell
python -m pytest
```

If all tests pass, you will see a green summary with no failures.

## 10. How To Customize

- Add more stocks to `backend/app/data/nse_popular_stocks.json`.
- Change default chart period in `frontend/streamlit_app.py`.
- Change backend port in `.env` (`BACKEND_PORT=8000`).
- Add new API fields in `backend/app/models/stock.py` and fetch them in `stock_service.py`.
