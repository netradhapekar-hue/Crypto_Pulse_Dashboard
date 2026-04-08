import requests
import pandas as pd
from datetime import datetime
import os

# ---------------- FETCH DATA ---------------- #
url = "https://api.coingecko.com/api/v3/coins/markets"

params = {
    "vs_currency": "usd",
    "order": "market_cap_desc",
    "per_page": 50,
    "page": 1
}

response = requests.get(url, params=params)

if response.status_code != 200:
    print("API Error:", response.status_code)
    print(response.text)
    exit()

data = response.json()

# 🔥 CRITICAL CHECK
if not isinstance(data, list):
    print("Unexpected API response:")
    print(data)
    exit()

df = pd.DataFrame(data)

# ---------------- SELECT COLUMNS ---------------- #
df = df[[
    "id", "symbol", "name",
    "current_price", "market_cap", "total_volume"
]]

# ---------------- CLEAN COLUMN NAMES ---------------- #
df.rename(columns={
    "current_price": "price",
    "total_volume": "volume"
}, inplace=True)

# ---------------- ADD TIMESTAMP ---------------- #
df["fetch_datetime"] = pd.Timestamp.now()

# ---------------- SAVE (APPEND MODE) ---------------- #
file_path = "crypto_raw.csv"

df.to_csv(
    file_path,
    mode='a',
    header=not os.path.exists(file_path),
    index=False
)

print("Data appended successfully")