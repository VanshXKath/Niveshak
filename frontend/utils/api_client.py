from __future__ import annotations

import os
from typing import Any

import requests
from dotenv import load_dotenv


load_dotenv()

BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000")


def fetch_json(endpoint: str, timeout: int = 45) -> dict[str, Any]:
    response = requests.get(f"{BACKEND_API_URL}{endpoint}", timeout=timeout)
    if response.status_code != 200:
        try:
            detail = response.json().get("detail", response.text)
        except ValueError:
            detail = response.text
        raise RuntimeError(detail)
    return response.json()


def post_json(endpoint: str, payload: dict[str, Any], timeout: int = 45) -> dict[str, Any]:
    response = requests.post(f"{BACKEND_API_URL}{endpoint}", json=payload, timeout=timeout)
    if response.status_code not in {200, 201}:
        try:
            detail = response.json().get("detail", response.text)
        except ValueError:
            detail = response.text
        raise RuntimeError(detail)
    return response.json()


def delete_request(endpoint: str, timeout: int = 30) -> None:
    response = requests.delete(f"{BACKEND_API_URL}{endpoint}", timeout=timeout)
    if response.status_code not in {200, 204}:
        raise RuntimeError(response.text)


def upload_pdf(endpoint: str, symbol: str, file_bytes: bytes, filename: str) -> dict[str, Any]:
    response = requests.post(
        f"{BACKEND_API_URL}{endpoint}",
        data={"symbol": symbol},
        files={"file": (filename, file_bytes, "application/pdf")},
        timeout=120,
    )
    if response.status_code != 200:
        raise RuntimeError(response.text)
    return response.json()
