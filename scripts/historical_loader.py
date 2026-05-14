import time
import requests
import pandas as pd

from datetime import datetime, timezone
from sqlalchemy import create_engine

# =====================================================
# DATABASE CONNECTION
# =====================================================

engine = create_engine(
    "postgresql://postgres:postgres@127.0.0.1:5432/crypto_pulse"
)

RAW_TABLE = "crypto_dashboard_raw"

# =====================================================
# DATE RANGE: 1 MARCH 2026 TO 5 MAY 2026
# =====================================================

START_DATE = datetime(2026, 3, 1, tzinfo=timezone.utc)
END_DATE = datetime(2026, 5, 5, tzinfo=timezone.utc)

DAYS = (END_DATE - START_DATE).days

print(f"Loading historical data from {START_DATE.date()} to {END_DATE.date()}")
print(f"Total days: {DAYS}")


def load_historical_data():
    top_url = "https://api.coingecko.com/api/v3/coins/markets"

    top_params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 30,
        "page": 1,
        "sparkline": False
    }

    response = requests.get(top_url, params=top_params, timeout=20)
    response.raise_for_status()

    coins = response.json()
    all_rows = []

    for coin in coins:
        coin_id = coin["id"]
        symbol = coin["symbol"].upper().strip()
        name = coin["name"].strip()
        image = coin.get("image")

        print(f"Fetching historical data for {name}")

        history_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"

        history_params = {
            "vs_currency": "usd",
            "days": DAYS,
            "interval": "daily"
        }

        success = False

        for attempt in range(5):
            try:
                history_response = requests.get(
                    history_url,
                    params=history_params,
                    timeout=30
                )

                if history_response.status_code == 429:
                    print(f"Rate limit hit for {name}. Waiting 60 seconds...")
                    time.sleep(60)
                    continue

                if history_response.status_code in [500, 502, 503, 504]:
                    print(f"Server error {history_response.status_code} for {name}. Retrying in 30 seconds...")
                    time.sleep(30)
                    continue

                history_response.raise_for_status()
                success = True
                break

            except requests.exceptions.RequestException as e:
                print(f"Request failed for {name}: {e}")
                print("Retrying in 30 seconds...")
                time.sleep(30)

        if not success:
            print(f"Skipping {name} after multiple failed attempts")
            continue

        history = history_response.json()

        prices = history.get("prices", [])
        market_caps = history.get("market_caps", [])
        volumes = history.get("total_volumes", [])
        for i in range(len(prices)):
            fetch_datetime = datetime.fromtimestamp(
                prices[i][0] / 1000,
                tz=timezone.utc
            )

            if START_DATE <= fetch_datetime <= END_DATE:
                all_rows.append({
                    "id": coin_id,
                    "symbol": symbol,
                    "name": name,
                    "image": image,
                    "price": prices[i][1],
                    "market_cap": market_caps[i][1] if i < len(market_caps) else None,
                    "volume": volumes[i][1] if i < len(volumes) else None,
                    "change_1h": None,
                    "change_24h": None,
                    "change_7d": None,
                    "fetch_datetime": fetch_datetime
                })

        time.sleep(10)

    df = pd.DataFrame(all_rows)

    if df.empty:
        print("No historical data collected")
        return

    df.to_sql(
        RAW_TABLE,
        engine,
        if_exists="append",
        index=False,
        method="multi"
    )

    print("✅ Historical data inserted into crypto_dashboard_raw")
    print(f"✅ Rows inserted: {len(df)}")


if __name__ == "__main__":
    load_historical_data()
