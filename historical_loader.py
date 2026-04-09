<<<<<<< HEAD
import requests
import pandas as pd
import os
import time
from datetime import datetime

# ---------------- FILE PATH ---------------- #
file_path = r"C:\Users\Intern_PBI\Desktop\Project1\crypto_raw.csv"

# ---------------- DATE RANGE ---------------- #
start_date = datetime(2026, 1, 1)
end_date = datetime.now()

from_timestamp = int(start_date.timestamp())
to_timestamp = int(end_date.timestamp())

# ---------------- STEP 1: FETCH TOP 50 COINS ---------------- #
print("Fetching top coins...")

url = "https://api.coingecko.com/api/v3/coins/markets"

params = {
    "vs_currency": "usd",
    "order": "market_cap_desc",
    "per_page": 50,
    "page": 1
}

response = requests.get(url, params=params)
data = response.json()

df_top = pd.DataFrame(data)

# ---------------- STEP 2: SELECT TOP 10 ---------------- #
top_coins = df_top["id"].head(10).tolist()
print("Top 10 Coins:", top_coins)

# ---------------- STEP 3: FETCH HISTORICAL DATA ---------------- #
all_data = []

for coin in top_coins:
    print(f"Fetching historical data for {coin}...")

    hist_url = f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart/range"

    hist_params = {
        "vs_currency": "usd",
        "from": from_timestamp,
        "to": to_timestamp
    }

    response = requests.get(hist_url, params=hist_params)
    hist_data = response.json()

    prices = hist_data.get("prices", [])

    temp_df = pd.DataFrame(prices, columns=["timestamp", "price"])

    # Convert timestamp
    temp_df["fetch_datetime"] = pd.to_datetime(temp_df["timestamp"], unit="ms")

    # Add coin ID
    temp_df["id"] = coin

    # ---------------- MERGE WITH COIN INFO ---------------- #
    coin_info = df_top[df_top["id"] == coin][[
        "id", "symbol", "name", "market_cap", "total_volume"
    ]]

    temp_df = temp_df.merge(coin_info, on="id", how="left")

    temp_df.rename(columns={
        "total_volume": "volume"
    }, inplace=True)

    temp_df = temp_df[[
        "id", "symbol", "name",
        "price", "market_cap", "volume",
        "fetch_datetime"
    ]]

    all_data.append(temp_df)

    time.sleep(1)  # avoid rate limit

# ---------------- STEP 4: COMBINE ---------------- #
historical_df = pd.concat(all_data, ignore_index=True)

# ---------------- STEP 5: SAVE ---------------- #
historical_df.to_csv(
    file_path,
    mode='a',
    header=not os.path.exists(file_path),
    index=False
)

=======
import requests
import pandas as pd
import os
import time
from datetime import datetime

# ---------------- FILE PATH ---------------- #
file_path = r"C:\Users\Intern_PBI\Desktop\Project1\crypto_raw.csv"

# ---------------- DATE RANGE ---------------- #
start_date = datetime(2026, 1, 1)
end_date = datetime.now()

from_timestamp = int(start_date.timestamp())
to_timestamp = int(end_date.timestamp())

# ---------------- STEP 1: FETCH TOP 50 COINS ---------------- #
print("Fetching top coins...")

url = "https://api.coingecko.com/api/v3/coins/markets"

params = {
    "vs_currency": "usd",
    "order": "market_cap_desc",
    "per_page": 50,
    "page": 1
}

response = requests.get(url, params=params)
data = response.json()

df_top = pd.DataFrame(data)

# ---------------- STEP 2: SELECT TOP 10 ---------------- #
top_coins = df_top["id"].head(10).tolist()
print("Top 10 Coins:", top_coins)

# ---------------- STEP 3: FETCH HISTORICAL DATA ---------------- #
all_data = []

for coin in top_coins:
    print(f"Fetching historical data for {coin}...")

    hist_url = f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart/range"

    hist_params = {
        "vs_currency": "usd",
        "from": from_timestamp,
        "to": to_timestamp
    }

    response = requests.get(hist_url, params=hist_params)
    hist_data = response.json()

    prices = hist_data.get("prices", [])

    temp_df = pd.DataFrame(prices, columns=["timestamp", "price"])

    # Convert timestamp
    temp_df["fetch_datetime"] = pd.to_datetime(temp_df["timestamp"], unit="ms")

    # Add coin ID
    temp_df["id"] = coin

    # ---------------- MERGE WITH COIN INFO ---------------- #
    coin_info = df_top[df_top["id"] == coin][[
        "id", "symbol", "name", "market_cap", "total_volume"
    ]]

    temp_df = temp_df.merge(coin_info, on="id", how="left")

    temp_df.rename(columns={
        "total_volume": "volume"
    }, inplace=True)

    temp_df = temp_df[[
        "id", "symbol", "name",
        "price", "market_cap", "volume",
        "fetch_datetime"
    ]]

    all_data.append(temp_df)

    time.sleep(1)  # avoid rate limit

# ---------------- STEP 4: COMBINE ---------------- #
historical_df = pd.concat(all_data, ignore_index=True)

# ---------------- STEP 5: SAVE ---------------- #
historical_df.to_csv(
    file_path,
    mode='a',
    header=not os.path.exists(file_path),
    index=False
)

>>>>>>> 2164dd4d82351bb59b28f0931699ba7accf94f26
print("✅ Historical data from Jan 2026 loaded successfully")