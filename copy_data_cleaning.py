def clean_crypto_data():
    import pandas as pd
    from sqlalchemy import create_engine

    engine = create_engine(
        "postgresql+psycopg2://postgres:postgres@host.docker.internal:5432/Crypto_Pulse"
    )

    RAW_TABLE = "crypto_dashboard_raw"
    CLEAN_TABLE = "crypto_dashboard_clean"

    df = pd.read_sql(f"SELECT * FROM {RAW_TABLE}", engine)

    df["fetch_datetime"] = pd.to_datetime(df["fetch_datetime"], utc=True)

    df = df.drop_duplicates(subset=["id", "fetch_datetime"])

    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["market_cap"] = pd.to_numeric(df["market_cap"], errors="coerce")
    df["volume"] = pd.to_numeric(df["volume"], errors="coerce")

    df = df.dropna(subset=["price", "market_cap"])
    df = df[(df["price"] > 0) & (df["market_cap"] > 0)]

    df["symbol"] = df["symbol"].str.upper().str.strip()
    df["name"] = df["name"].str.strip()

    df["fetch_date"] = df["fetch_datetime"].dt.date
    df["fetch_time"] = df["fetch_datetime"].dt.time

    df = df.sort_values(by=["id", "fetch_datetime"])

    df["is_latest"] = df.groupby("id")["fetch_datetime"].transform("max") == df["fetch_datetime"]
    df["is_latest"] = df["is_latest"].astype(int)

    df.to_sql(
        CLEAN_TABLE,
        engine,
        if_exists="replace",
        index=False
    )

    print("✅ Clean data saved")