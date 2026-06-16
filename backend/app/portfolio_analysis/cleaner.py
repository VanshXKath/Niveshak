import pandas as pd


def check_col(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        raise ValueError("The uploaded file is empty or invalid.")
    return df


def normalise_col(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = df.columns.astype(str).str.lower().str.replace("\n", " ").str.replace("\u00a0", "").str.strip()
    return df


def standardise_col(df: pd.DataFrame) -> pd.DataFrame:
    column_mapping = {
        "instrument": "symbol",
        "symbol": "symbol",
        "stock": "symbol",
        "security": "symbol",
        "scrip": "symbol",
        "qty": "quantity",
        "qty.": "quantity",
        "quantity": "quantity",
        "units": "quantity",
        "shares": "quantity",
        "avg cost": "avg_cost",
        "avg. cost": "avg_cost",
        "average cost": "avg_cost",
        "buy price": "avg_cost",
        "rate": "avg_cost",
        "invested": "invested",
        "investment": "invested",
        "total cost": "invested",
        "cur. val": "current_value",
        "cur val": "current_value",
        "current value": "current_value",
        "market value": "current_value",
        "ltp": "ltp",
        "p&l": "pnl",
        "profit": "pnl",
        "loss": "pnl",
        "gain": "pnl",
    }
    return df.rename(columns=column_mapping)


def smart_col(df: pd.DataFrame) -> pd.DataFrame:
    keyword_map = {
        "symbol": ["instrument", "symbol", "stock", "scrip", "security"],
        "quantity": ["qty", "quantity", "share", "unit"],
        "avg_cost": ["avg", "cost", "price", "rate"],
        "invested": ["invested", "amount", "value", "cost"],
        "current_value": ["current", "market", "value"],
        "pnl": ["p&l", "profit", "loss", "gain"],
        "ltp": ["ltp", "price"],
    }
    existing_cols = set(df.columns)
    new_columns: dict[str, str] = {}
    for col in df.columns:
        if col in keyword_map:
            continue
        for standard_col, keywords in keyword_map.items():
            if standard_col in existing_cols:
                continue
            if any(keyword in col for keyword in keywords):
                new_columns[col] = standard_col
                break
    return df.rename(columns=new_columns)


def remove_duplicate_columns(df: pd.DataFrame) -> pd.DataFrame:
    return df.loc[:, ~df.columns.duplicated()]


def filter_valid_rows(df: pd.DataFrame) -> pd.DataFrame:
    if "symbol" in df.columns:
        df = df[df["symbol"].notna()]
        df = df[df["symbol"].astype(str).str.len() > 0]
    if "quantity" in df.columns:
        df = df[df["quantity"].notna()]
    return df.reset_index(drop=True)


def clean_holdings(df: pd.DataFrame) -> pd.DataFrame:
    df = check_col(df)
    df = normalise_col(df)
    df = standardise_col(df)
    df = smart_col(df)
    df = remove_duplicate_columns(df)
    df = filter_valid_rows(df)
    return df
