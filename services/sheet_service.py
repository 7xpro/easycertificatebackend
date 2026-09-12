import pandas as pd


def read_excel_file(file_path):
    """
    Reads an Excel file and returns recipient data as {"name": [...], "email": [...]}.
    Raises ValueError on missing columns, empty data, or malformed rows.
    """
    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        raise ValueError(f"Could not read Excel file: {e}")

    # Normalize column names so "name"/"Name "/"NAME" all work
    df.columns = [str(c).strip().lower() for c in df.columns]

    required = {"name", "email"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required column(s): {', '.join(missing)}")

    if df.empty:
        raise ValueError("Excel file has no data rows")

    # Drop rows with blank name/email instead of passing NaN downstream
    df = df.dropna(subset=["name", "email"])
    if df.empty:
        raise ValueError("No valid rows found (all name/email cells were blank)")

    df["name"] = df["name"].astype(str).str.strip()
    df["email"] = df["email"].astype(str).str.strip()

    return {"name": df["name"].tolist(), "email": df["email"].tolist()}