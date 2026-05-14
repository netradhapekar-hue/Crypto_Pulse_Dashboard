def fetch_crypto_data():

    import requests
    import pandas as pd

    from datetime import datetime, timezone
    from sqlalchemy.exc import SQLAlchemyError

    # =====================================================
    # DATABASE CONNECTION
    # =====================================================

    from dotenv import load_dotenv
    import os
    from sqlalchemy import create_engine

    load_dotenv()

    engine = create_engine(os.getenv("DATABASE_URL"))

    TABLE_NAME = "crypto_dashboard_raw"

    # =====================================================
    # COINGECKO API
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

    try:
        response = requests.get(
            url,
            params=params,
            timeout=20
        )

        response.raise_for_status()

    except requests.exceptions.Timeout:
        raise Exception("CoinGecko API request timed out")

    except requests.exceptions.ConnectionError:
        raise Exception("Network connection error while calling CoinGecko API")

    except requests.exceptions.HTTPError as e:
        raise Exception(f"CoinGecko API HTTP error: {e}")

    except requests.exceptions.RequestException as e:
        raise Exception(f"CoinGecko API request failed: {e}")

    # =====================================================
    # JSON TO DATAFRAME
    # =====================================================

    try:
        data = response.json()

        if not data:
            raise ValueError("CoinGecko API returned empty data")

        df = pd.DataFrame(data)

    except ValueError as e:
        raise Exception(f"Invalid API response: {e}")

    # =====================================================
    # REQUIRED COLUMN VALIDATION
    # =====================================================

    required_columns = [
        "id",
        "symbol",
        "name",
        "image",
        "current_price",
        "market_cap",
        "total_volume",
        "price_change_percentage_1h_in_currency",
        "price_change_percentage_24h",
        "price_change_percentage_7d_in_currency"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        raise Exception(f"Missing columns in API data: {missing_columns}")

    # =====================================================
    # KEEP REQUIRED COLUMNS
    # =====================================================

    df = df[required_columns]

    # =====================================================
    # RENAME COLUMNS
    # =====================================================

    df.rename(columns={
        "current_price": "price",
        "total_volume": "volume",
        "price_change_percentage_1h_in_currency": "change_1h",
        "price_change_percentage_24h": "change_24h",
        "price_change_percentage_7d_in_currency": "change_7d"
    }, inplace=True)

    # =====================================================
    # CLEAN DATA
    # =====================================================

    try:
        df["symbol"] = df["symbol"].astype(str).str.upper().str.strip()
        df["name"] = df["name"].astype(str).str.strip()

        numeric_columns = [
            "price",
            "market_cap",
            "volume",
            "change_1h",
            "change_24h",
            "change_7d"
        ]

        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    except Exception as e:
        raise Exception(f"Data cleaning failed: {e}")

    # =====================================================
    # FETCH TIMESTAMP
    # =====================================================

    current_time = datetime.now(timezone.utc)

    df["fetch_datetime"] = current_time

    # =====================================================
    # INSERT INTO POSTGRES
    # =====================================================

    try:
        df.to_sql(
            TABLE_NAME,
            engine,
            if_exists="append",
            index=False,
            method="multi"
        )

    except SQLAlchemyError as e:
        raise Exception(f"Database insertion failed: {e}")

    except Exception as e:
        raise Exception(f"Unexpected database error: {e}")

    # =====================================================
    # SUCCESS MESSAGE
    # =====================================================

    print("✅ Raw data inserted successfully")
    print(f"✅ Rows inserted: {len(df)}")
    print("✅ Image URLs included")
    print(f"✅ Fetch time: {current_time}")


if __name__ == "__main__":
    fetch_crypto_data()