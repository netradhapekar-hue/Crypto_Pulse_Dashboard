import pandas as pd
from sqlalchemy import create_engine

# ---------------- CONFIG ---------------- #

engine = create_engine(
    "postgresql+psycopg2://postgres:postgres@localhost:5432/Crypto_Pulse"
)

RAW_TABLE = "crypto_dashboard_raw"
CLEAN_TABLE = "crypto_dashboard_clean"

# ---------------- LOAD DATA ---------------- #

df = pd.read_sql(f"SELECT * FROM {RAW_TABLE}", engine)

print("Data Types Before Cleaning:")
print(df.dtypes)

# ---------------- CLEANING ---------------- #

# Datetime
df["fetch_datetime"] = pd.to_datetime(df["fetch_datetime"], utc=True)

# Remove duplicates
df = df.drop_duplicates(subset=["id", "fetch_datetime"])

# Numeric cleaning
df["price"] = pd.to_numeric(df["price"], errors="coerce")
df["market_cap"] = pd.to_numeric(df["market_cap"], errors="coerce")
df["volume"] = pd.to_numeric(df["volume"], errors="coerce")

# Remove invalid
df = df.dropna(subset=["price", "market_cap"])
df = df[(df["price"] > 0) & (df["market_cap"] > 0)]

# Standardize text
df["symbol"] = df["symbol"].str.upper().str.strip()
df["name"] = df["name"].str.strip()

# ---------------- DERIVED COLUMNS ---------------- #

df["fetch_date"] = df["fetch_datetime"].dt.date
df["fetch_time"] = df["fetch_datetime"].dt.time

# Sort
df = df.sort_values(by=["id", "fetch_datetime"])

# ---------------- IS_LATEST FLAG ---------------- #

df["is_latest"] = df.groupby("id")["fetch_datetime"].transform("max") == df["fetch_datetime"]
df["is_latest"] = df["is_latest"].astype(int)

# ---------------- SAVE CLEAN TABLE ---------------- #

df.to_sql(
    CLEAN_TABLE,
    engine,
    if_exists="replace",
    index=False
)

print("✅ Clean data saved to crypto_dashboard_clean")

# ---------------- OPTIONAL BACKUP ---------------- #

df.to_csv("crypto_clean_backup.csv", index=False)

print("📁 Backup created")

# ---------------- DEBUG ---------------- #

print("\nLatest timestamp:", df["fetch_datetime"].max())
print("\nSample:")
print(df.head())