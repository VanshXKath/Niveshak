from __future__ import annotations

from io import BytesIO

import pandas as pd

POSSIBLE_HEADER_KEYWORDS = [
    "stock",
    "instrument",
    "symbol",
    "scrip",
    "quantity",
    "qty",
    "units",
    "avg",
    "average",
    "buy",
    "price",
    "cost",
]


def detect_header_row(file_bytes: bytes) -> int:
    raw_df = pd.read_excel(BytesIO(file_bytes), header=None)
    for index in range(len(raw_df)):
        row = raw_df.iloc[index].astype(str).str.lower().tolist()
        match_count = sum(any(keyword in cell for keyword in POSSIBLE_HEADER_KEYWORDS) for cell in row)
        if match_count >= 3:
            return index
    raise ValueError("Could not detect holdings table header in the Excel file.")


def read_holdings_file(file_bytes: bytes, filename: str) -> pd.DataFrame:
    lowered = filename.lower()
    if lowered.endswith(".csv"):
        return pd.read_csv(BytesIO(file_bytes))
    if lowered.endswith(".xlsx"):
        header_row = detect_header_row(file_bytes)
        return pd.read_excel(BytesIO(file_bytes), header=header_row)
    raise ValueError("Unsupported file format. Upload CSV or XLSX from your broker.")
