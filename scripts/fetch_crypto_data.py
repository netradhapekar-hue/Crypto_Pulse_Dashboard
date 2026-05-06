def fetch_crypto_data():

    import requests
    import pandas as pd

    from datetime import datetime, timezone

    from sqlalchemy import create_engine

    # =====================================================
    # 🔥 DATABASE CONNECTION
    # =====================================================

    engine = create_engine(
        "postgresql://postgres:postgres@127.0.0.1:5432/crypto_pulse"
    )

    TABLE_NAME = "crypto_dashboard_raw"

    # =====================================================
    # 🔥 COINGECKO API
    # =====================================================

    url = "https://api.coingecko.com/api/v3/coins/markets"

    params = {

        "vs_currency": "usd",

        "order": "market_cap_desc",

        "per_page": 50,

        "page": 1,

        "sparkline": False,

        "price_change_percentage": "1h,24h,7d"
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:

        raise Exception(f"API Error: {response.status_code}")

    # =====================================================
    # 🔥 JSON TO DATAFRAME
    # =====================================================

    data = response.json()

    df = pd.DataFrame(data)

    # =====================================================
    # 🔥 KEEP REQUIRED COLUMNS
    # =====================================================

    df = df[[

        "id",

        "symbol",

        "name",

        "image",   # 🔥 ADDED

        "current_price",

        "market_cap",

        "total_volume",

        "price_change_percentage_1h_in_currency",

        "price_change_percentage_24h",

        "price_change_percentage_7d_in_currency"
    ]]

    # =====================================================
    # 🔥 RENAME COLUMNS
    # =====================================================

    df.rename(columns={

        "current_price": "price",

        "total_volume": "volume",

        "price_change_percentage_1h_in_currency": "change_1h",

        "price_change_percentage_24h": "change_24h",

        "price_change_percentage_7d_in_currency": "change_7d"

    }, inplace=True)

    # =====================================================
    # 🔥 CLEAN DATA
    # =====================================================

    df["symbol"] = df["symbol"].str.upper().str.strip()

    df["name"] = df["name"].str.strip()

    # =====================================================
    # 🔥 FETCH TIMESTAMP
    # =====================================================

    current_time = datetime.now(timezone.utc)

    df["fetch_datetime"] = current_time

    # =====================================================
    # 🔥 INSERT INTO POSTGRES
    # =====================================================

    df.to_sql(

        TABLE_NAME,

        engine,

        if_exists="append",

        index=False,

        method="multi"
    )

    # =====================================================
    # 🔥 SUCCESS MESSAGE
    # =====================================================

    print("✅ Raw data inserted successfully")

    print(f"✅ Rows inserted: {len(df)}")

    print("✅ Image URLs included")