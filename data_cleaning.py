import pandas as pd

# ---------------- LOAD RAW DATA ---------------- #
df = pd.read_csv("crypto_raw.csv")

# ---------------- DATA TYPE CHECK ---------------- #
print("Data Types Before Cleaning:")
print(df.dtypes)

# ---------------- CLEANING ---------------- #

# ✅ Remove duplicates ONLY for same coin + same timestamp
df = df.drop_duplicates(subset=["id", "fetch_datetime"])

# Handle missing values
df = df.dropna(subset=["price", "market_cap"])

# Standardize text
df["symbol"] = df["symbol"].str.upper().str.strip()
df["name"] = df["name"].str.strip()

# Convert numeric fields
df["price"] = pd.to_numeric(df["price"], errors="coerce")
df["market_cap"] = pd.to_numeric(df["market_cap"], errors="coerce")
df["volume"] = pd.to_numeric(df["volume"], errors="coerce")

# Fill missing numeric values with 0 and convert to integers
df["market_cap"] = df["market_cap"].fillna(0).astype("int64")
df["volume"] = df["volume"].fillna(0).astype("int64")

# Convert date and time fields to datetime
df["fetch_datetime"] = pd.to_datetime(df["fetch_datetime"], errors="coerce")

# ✅ Combine into single datetime (VERY IMPORTANT for Power BI)
df["fetch_datetime"] = pd.to_datetime(df["fetch_datetime"], errors="coerce")


# Remove invalid values
df = df[(df["price"] > 0) & (df["market_cap"] > 0)]

# Rename columns
df = df.rename(columns={
    "current_price": "price",
    "total_volume": "volume"
})

# ---------------- SORT DATA (IMPORTANT FOR TREND) ---------------- #
df = df.sort_values(by=["id", "fetch_datetime"])

# ---------------- SAVE CLEAN DATA ---------------- #
# ✅ OVERWRITE CLEAN FILE (latest clean view)
df.to_csv("crypto_clean.csv", index=False)

print("Clean data saved (overwritten) as crypto_clean.csv")

# ---------------- DATA TYPE CHECK AFTER CLEANING ---------------- #
print("Data Types After Cleaning:")
print(df.dtypes)