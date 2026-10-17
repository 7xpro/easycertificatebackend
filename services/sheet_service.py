import pandas as pd

def read_excel_file(file_path):
    
    
    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        raise ValueError(f"Could not read Excel file: {e}")

    # Normalize column names so "name"/"Name "/"NAME" all work
    df.columns = [str(c).strip().lower() for c in df.columns]

   

    if df.empty:
        raise ValueError("Excel file has no data rows")

    # Drop rows with blank name/email instead of passing NaN downstream
    df = df.dropna(subset=["name", "email"])
    if df.empty:
        raise ValueError("No valid rows found (all name/email cells were blank)")
    id=df["id"].astype(str).str.strip()
    email=df["email"].astype(str).str.strip()
    name=df["name"].astype(str).str.strip()
    date=df["date"].astype(str).str.strip()

    
  
    return {
        

        "ID": id.tolist(),
        "Name": name.tolist(),  
        "Email": email.tolist(),
        "Date": date.tolist(),
    }