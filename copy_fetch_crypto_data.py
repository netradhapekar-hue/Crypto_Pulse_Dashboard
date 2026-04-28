def fetch_crypto_data():
    import requests
    import pandas as pd
    from datetime import datetime, timezone
    from sqlalchemy import create_engine

    engine = create_engine(
        "postgresql+psycopg2://postgres:postgres@host.docker.internal:5432/Crypto_Pulse"
    )

    TABLE_NAME = "crypto_dashboard_raw"

    url = "https://api.coingecko.com/api/v3/coins/markets"

    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 50,
        "page": 1
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise Exception(f"API Error: {response.status_code}")

    data = response.json()
    df = pd.DataFrame(data)

    df = df[[
        "id", "symbol", "name",
        "current_price", "market_cap", "total_volume"
    ]]

    df.rename(columns={
        "current_price": "price",
        "total_volume": "volume"
    }, inplace=True)

    df["symbol"] = df["symbol"].str.upper().str.strip()
    df["name"] = df["name"].str.strip()

    current_time = datetime.now(timezone.utc)
    df["fetch_datetime"] = current_time

    df.to_sql(
        TABLE_NAME,
        engine,
        if_exists="append",
        index=False,
        method="multi"
    )

    print("✅ Raw data inserted")