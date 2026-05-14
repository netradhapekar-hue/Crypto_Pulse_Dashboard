from flask import Flask, jsonify, request
import psycopg2
from psycopg2 import Error
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# =========================================================
# DB CONNECTION
# =========================================================

def get_connection():

    try:

        return psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT", "5432")
        )

    except Error as e:

        print(f"❌ Database connection failed: {e}")

        raise


# =========================================================
# ERROR RESPONSE
# =========================================================

def error_response(message, error, status_code=500):

    print(f"❌ {message}: {error}")

    return jsonify({
        "error": message,
        "details": str(error)
    }), status_code
# =========================================================
# HOME ROUTE
# =========================================================

@app.route('/')
def home():
    return "Crypto Dashboard API Running 🚀"


# =========================================================
# KPI SUMMARY
# =========================================================

@app.route('/summary')
def summary():
    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT 
                AVG(price),
                MAX(price),
                MIN(price),
                COUNT(*)
            FROM crypto_dashboard_clean
            WHERE price > 0
        """)

        avg_price, max_price, min_price, total = cur.fetchone()

        return jsonify({
            "avg_price": float(avg_price or 0),
            "max_price": float(max_price or 0),
            "min_price": float(min_price or 0),
            "total_records": total
        })

    except Exception as e:
        return error_response("Failed to fetch summary data", e)

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


# =========================================================
# TRENDING
# =========================================================

@app.route('/trending')
def trending():
    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT 
                symbol,
                name,
                image,
                (MAX(price) - MIN(price)) / NULLIF(MIN(price),0) * 100 AS change
            FROM crypto_dashboard_clean
            GROUP BY symbol, name, image
            ORDER BY change DESC
            LIMIT 5
        """)

        rows = cur.fetchall()

        result = []

        for r in rows:
            result.append({
                "symbol": r[0],
                "name": r[1],
                "image": r[2],
                "change": float(r[3]) if r[3] else 0
            })

        return jsonify(result)

    except Exception as e:
        return error_response("Failed to fetch trending data", e)

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


# =========================================================
# TOP ASSETS
# =========================================================

@app.route('/top-assets')
def top_assets():
    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT 
                symbol,
                image
            FROM crypto_dashboard_clean
            GROUP BY symbol, image
            ORDER BY AVG(price) DESC
            LIMIT 5
        """)

        coins = cur.fetchall()

        result = []

        for coin in coins:
            symbol = coin[0]
            image = coin[1]

            cur.execute("""
                SELECT fetch_datetime, price
                FROM crypto_dashboard_clean
                WHERE symbol = %s
                ORDER BY fetch_datetime DESC
                LIMIT 20
            """, (symbol,))

            rows = cur.fetchall()[::-1]

            prices = [float(r[1]) for r in rows]

            result.append({
                "coin": symbol,
                "image": image,
                "latest_price": prices[-1] if prices else 0,
                "trend": prices
            })

        return jsonify(result)

    except Exception as e:
        return error_response("Failed to fetch top assets", e)

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


# =========================================================
# TABLE DATA
# =========================================================

@app.route('/table')
def table():
    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT 
                symbol,
                image,
                MAX(price) AS latest_price,
                MIN(price) AS min_price,
                AVG(volume) AS volume,
                AVG(market_cap) AS market_cap
            FROM crypto_dashboard_clean
            WHERE fetch_datetime >= NOW() - INTERVAL '7 days'
            GROUP BY symbol, image
            ORDER BY latest_price DESC
            LIMIT 10
        """)

        rows = cur.fetchall()

        result = []

        for r in rows:
            symbol = r[0]
            image = r[1]
            latest_price = float(r[2] or 0)
            min_price = float(r[3] or 0)
            volume = float(r[4] or 0)
            market_cap = float(r[5] or 0)

            change = latest_price - min_price

            change_percent = (
                (change / min_price) * 100
                if min_price != 0
                else 0
            )

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
                "image": image,
                "price": latest_price,
                "change_1h": change_percent / 7,
                "change_24h": change_percent / 3,
                "change_7d": change_percent,
                "volume": volume,
                "market_cap": market_cap,
                "trend": trend
            })

        return jsonify(result)

    except Exception as e:
        return error_response("Failed to fetch table data", e)

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


# =========================================================
# FILTER DATA
# =========================================================

@app.route('/filter')
def filter_data():
    conn = None
    cur = None

    try:
        coin = request.args.get('coin')
        start = request.args.get('start')
        end = request.args.get('end')

        conn = get_connection()
        cur = conn.cursor()

        query = """
            SELECT 
                symbol,
                image,
                price,
                fetch_datetime
            FROM crypto_dashboard_clean
            WHERE 1=1
        """

        params = []

        if coin:
            query += " AND symbol = %s"
            params.append(coin.upper())

        if start and end:
            query += " AND fetch_datetime BETWEEN %s AND %s"
            params.extend([start, end])

        query += """
            ORDER BY fetch_datetime DESC
            LIMIT 100
        """

        cur.execute(query, tuple(params))

        rows = cur.fetchall()

        result = []

        for r in rows:
            result.append({
                "coin": r[0],
                "image": r[1],
                "price": float(r[2]),
                "date": str(r[3])
            })

        return jsonify(result)

    except Exception as e:
        return error_response("Failed to fetch filtered data", e)

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


# =========================================================
# TOP GAINERS
# =========================================================

@app.route('/top-gainers')
def top_gainers():
    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT 
                symbol,
                image,
                MAX(price) - MIN(price) AS change
            FROM crypto_dashboard_clean
            GROUP BY symbol, image
            ORDER BY change DESC
            LIMIT 5
        """)

        rows = cur.fetchall()

        result = []

        for r in rows:
            result.append({
                "coin": r[0],
                "image": r[1],
                "change": float(r[2] or 0)
            })

        return jsonify(result)

    except Exception as e:
        return error_response("Failed to fetch top gainers", e)

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


# =========================================================
# MAIN CHART TREND
# =========================================================

@app.route('/trend/<coin>')
def trend_chart(coin):
    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT 
                fetch_datetime,
                price
            FROM crypto_dashboard_clean
            WHERE symbol = %s
            ORDER BY fetch_datetime ASC
            LIMIT 100
        """, (coin.upper(),))

        rows = cur.fetchall()

        result = []

        for r in rows:
            result.append({
                "date": str(r[0]),
                "price": float(r[1])
            })

        return jsonify(result)

    except Exception as e:
        return error_response("Failed to fetch trend chart data", e)

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


# =========================================================
# RUN SERVER
# =========================================================

if __name__ == "__main__":
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )