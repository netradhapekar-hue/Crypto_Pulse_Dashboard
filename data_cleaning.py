import pandas as pd

# ---------------- LOAD RAW DATA ---------------- #
df = pd.read_csv("crypto_raw.csv")

#----------------- DATA TYPE CHECK ---------------- #
print("Data Types Before Cleaning:")
print(df.dtypes)

# ---------------- CLEANING ---------------- #

# Remove duplicates
df = df.drop_duplicates(subset=["id"])

# Handle missing values
df = df.dropna(subset=["current_price", "market_cap"])

# Standardize text
df["symbol"] = df["symbol"].str.upper().str.strip()
df["name"] = df["name"].str.strip()

# Convert numeric fields
df["current_price"] = pd.to_numeric(df["current_price"], errors="coerce")
df["market_cap"] = pd.to_numeric(df["market_cap"], errors="coerce")
df["total_volume"] = pd.to_numeric(df["total_volume"], errors="coerce")

# Fill missing numeric values with 0 and convert to integers
df["market_cap"] = df["market_cap"].fillna(0).astype("int64")
df["total_volume"] = df["total_volume"].fillna(0).astype("int64")

# Convert date and time fields to datetime
df["fetch_time"] = pd.to_datetime(df["fetch_time"])
df["fetch_date"] = pd.to_datetime(df["fetch_date"])

# Remove invalid values
df = df[(df["current_price"] > 0) & (df["market_cap"] > 0)]

# Rename columns
df = df.rename(columns={
    "current_price": "price",
    "total_volume": "volume"
})

# ---------------- SAVE CLEAN DATA ---------------- #
df.to_csv("crypto_clean.csv", index=False)

print("Clean data saved as crypto_clean.csv")

#---------------- DATA TYPE CHECK AFTER CLEANING ---------------- #
print("Data Types After Cleaning:")
print(df.dtypes)