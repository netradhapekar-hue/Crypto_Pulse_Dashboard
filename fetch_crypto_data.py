import requests
import pandas as pd
from datetime import datetime

# ---------------- FETCH DATA ---------------- #
url = "https://api.coingecko.com/api/v3/coins/markets"

params = {
    "vs_currency": "usd",
    "order": "market_cap_desc",
    "per_page": 50,
    "page": 1
}

response = requests.get(url, params=params)
data = response.json()

df = pd.DataFrame(data)

# ---------------- SELECT COLUMNS ---------------- #
df = df[[
    "id", "symbol", "name",
    "current_price", "market_cap", "total_volume"
]]

# ---------------- ADD DATE & TIME ---------------- #
current_time = datetime.now()

df["fetch_time"] = current_time.strftime("%H:%M:%S")
df["fetch_date"] = current_time.strftime("%d-%m-%Y")

# ---------------- SAVE RAW DATA ---------------- #
df.to_csv("crypto_raw.csv", index=False)

print("Raw data saved as crypto_raw.csv")