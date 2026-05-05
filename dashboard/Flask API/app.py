from flask import Flask, jsonify, request
import psycopg2
import random
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 🔹 DB CONNECTION
def get_connection():
    return psycopg2.connect(
        dbname="crypto_pulse",
        user="postgres",
        password="postgres",
        host="localhost",
        port="5432"
    )

# =========================================================
# 🔥 HOME ROUTE
# =========================================================
@app.route('/')
def home():
    return "Crypto Dashboard API Running 🚀"

# =========================================================
# 🔥 KPI SUMMARY (Top Cards)
# =========================================================
@app.route('/summary')
def summary():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            AVG(price),
            MAX(price),
            MIN(price),
            COUNT(*)
        FROM crypto_dashboard_clean
    """)

    avg_price, max_price, min_price, total = cur.fetchone()

    cur.close()
    conn.close()

    return jsonify({
        "avg_price": float(avg_price or 0),
        "max_price": float(max_price or 0),
        "min_price": float(min_price or 0),
        "total_records": total
    })


# ========================================================
# TRENDING SECTION -> FINDS THE LATEST TRENDING COINS:
# =======================================================

@app.route('/trending')
def trending():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT symbol, name,
               (MAX(price) - MIN(price)) / NULLIF(MIN(price),0) * 100 AS change
        FROM crypto_dashboard_clean
        WHERE fetch_datetime >= NOW() - INTERVAL '1 day'
        GROUP BY symbol, name
        ORDER BY change DESC
        LIMIT 5
    """)

    rows = cur.fetchall()

    result = [
        {
            "symbol": r[0],
            "name": r[1],
            "change": float(r[2]) if r[2] else 0
        }
        for r in rows
    ]

    cur.close()
    conn.close()

    return jsonify(result)

# =========================================================
# 🔥 TREND (FIXED: date → fetch_datetime, coin → symbol)
# =========================================================
@app.route('/top-assets')
def top_assets():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT symbol
        FROM crypto_dashboard_clean
        GROUP BY symbol
        ORDER BY AVG(price) DESC
        LIMIT 5
    """)

    coins = [r[0] for r in cur.fetchall()]

    result = []

    for coin in coins:
        cur.execute("""
            SELECT fetch_datetime, price
            FROM crypto_dashboard_clean
            WHERE symbol = %s
            ORDER BY fetch_datetime DESC
            LIMIT 20
        """, (coin,))

        rows = cur.fetchall()[::-1]  # reverse for chart

        prices = [float(r[1]) for r in rows]

        result.append({
            "coin": coin,
            "latest_price": prices[-1] if prices else 0,
            "trend": prices
        })

    cur.close()
    conn.close()

    return jsonify(result)
# =========================================================
# 🔥 TABLE DATA (FIXED)
# =========================================================

@app.route('/table')
def table():
    conn = get_connection()
    cur = conn.cursor()

    # 🔥 Main aggregated query (includes volume & market cap)
    cur.execute("""
        SELECT 
            symbol,
            MAX(price) AS latest_price,
            MIN(price) AS min_price,
            AVG(volume) AS volume,
            AVG(market_cap) AS market_cap
        FROM crypto_dashboard_clean
        WHERE fetch_datetime >= NOW() - INTERVAL '7 days'
        GROUP BY symbol
        ORDER BY latest_price DESC
        LIMIT 10
    """)

    rows = cur.fetchall()
    result = []

    for r in rows:
        symbol = r[0]
        latest_price = float(r[1])
        min_price = float(r[2])
        volume = float(r[3] or 0)
        market_cap = float(r[4] or 0)

        # 🔥 % change calculation
        change = latest_price - min_price
        change_percent = (change / min_price * 100) if min_price != 0 else 0

        # 🔥 Trend data (last 20 points)
        cur.execute("""
            SELECT price
            FROM crypto_dashboard_clean
            WHERE symbol = %s
            ORDER BY fetch_datetime DESC
            LIMIT 20
        """, (symbol,))

        trend_rows = cur.fetchall()[::-1]
        trend = [float(x[0]) for x in trend_rows]

        result.append({
            "coin": symbol,
            "price": latest_price,
            "change_1h": change_percent / 7,    # approx
            "change_24h": change_percent / 3,   # approx
            "change_7d": change_percent,
            "volume": volume,
            "market_cap": market_cap,
            "trend": trend
        })

    cur.close()
    conn.close()

    return jsonify(result)

# =========================================================
# 🔥 FILTER DATA (FIXED)
# =========================================================
@app.route('/filter')
def filter_data():
    coin = request.args.get('coin')
    start = request.args.get('start')
    end = request.args.get('end')

    conn = get_connection()
    cur = conn.cursor()

    query = """
        SELECT symbol, price, fetch_datetime
        FROM crypto_dashboard_clean
        WHERE 1=1
    """
    params = []

    if coin:
        query += " AND symbol = %s"
        params.append(coin)

    if start and end:
        query += " AND fetch_datetime BETWEEN %s AND %s"
        params.extend([start, end])

    query += " ORDER BY fetch_datetime DESC LIMIT 100"

    cur.execute(query, tuple(params))
    rows = cur.fetchall()

    result = [
        {
            "coin": r[0],
            "price": float(r[1]),
            "date": str(r[2])
        }
        for r in rows
    ]

    cur.close()
    conn.close()

    return jsonify(result)

# =========================================================
# 🔥 TOP GAINERS (FIXED)
# =========================================================
@app.route('/top-gainers')
def top_gainers():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT symbol, MAX(price) - MIN(price) AS change
        FROM crypto_dashboard_clean
        GROUP BY symbol
        ORDER BY change DESC
        LIMIT 5
    """)

    rows = cur.fetchall()

    result = [
        {"coin": r[0], "change": float(r[1])}
        for r in rows
    ]

    cur.close()
    conn.close()

    return jsonify(result)

# =========================================================
# 🔥 RUN SERVER
# =========================================================
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
