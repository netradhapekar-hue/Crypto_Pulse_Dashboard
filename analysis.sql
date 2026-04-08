-- ==========================
-- 0. BASIC DATA CHECK
-- ==========================

SELECT COUNT(*) FROM crypto_data;

-- ==========================
-- 1. DATA VALIDATION CHECKS
-- ==========================

-- Total rows
SELECT COUNT(*) AS total_rows FROM crypto_data;

-- Null checks
SELECT 
    COUNT(*) FILTER (WHERE price IS NULL) AS null_price,
    COUNT(*) FILTER (WHERE market_cap IS NULL) AS null_market_cap,
    COUNT(*) FILTER (WHERE volume IS NULL) AS null_volume
FROM crypto_data;

-- Duplicate IDs (important for time-series → expect duplicates)
SELECT id, COUNT(*)
FROM crypto_data
GROUP BY id
HAVING COUNT(*) > 1;

-- ==========================
-- 2. MARKET OVERVIEW KPIs
-- ==========================

SELECT 
    COUNT(*) AS total_coins,
    ROUND(AVG(price),2) AS avg_price,
    SUM(market_cap) AS total_market_cap,
    SUM(volume) AS total_volume,
    MAX(price) AS highest_price,
    MIN(price) AS lowest_price
FROM crypto_data;

-- ==========================
-- 3. MARKET LEADERS
-- ==========================

SELECT name, market_cap
FROM crypto_data
ORDER BY market_cap DESC
LIMIT 10;

SELECT name, volume
FROM crypto_data
ORDER BY volume DESC
LIMIT 10;

SELECT name, price
FROM crypto_data
ORDER BY price DESC
LIMIT 10;

-- ==========================
-- 4. LOWEST PERFORMERS
-- ==========================

SELECT name, market_cap
FROM crypto_data
ORDER BY market_cap ASC
LIMIT 10;

SELECT name, volume
FROM crypto_data
ORDER BY volume ASC
LIMIT 10;

SELECT name, price
FROM crypto_data
ORDER BY price ASC
LIMIT 10;

-- ==========================
-- 5. MARKET DOMINANCE
-- ==========================

SELECT 
    name,
    market_cap,
    ROUND(market_cap * 100.0 / SUM(market_cap) OVER(), 2) AS market_share_pct
FROM crypto_data
ORDER BY market_cap DESC
LIMIT 10;

-- ==========================
-- 6. LIQUIDITY ANALYSIS
-- ==========================

SELECT 
    name,
    volume,
    market_cap,
    ROUND(volume * 1.0 / NULLIF(market_cap, 0), 4) AS volume_to_marketcap_ratio
FROM crypto_data
ORDER BY volume_to_marketcap_ratio DESC
LIMIT 10;

-- ================================
-- 7. SEGMENTATION ANALYSIS
-- ================================

SELECT 
    CASE 
        WHEN price > 10000 THEN 'High Value'
        WHEN price BETWEEN 1000 AND 10000 THEN 'Mid Value'
        ELSE 'Low Value'
    END AS price_category,
    COUNT(*) AS total_coins
FROM crypto_data
WHERE price > 0
GROUP BY price_category;

SELECT 
    CASE 
        WHEN market_cap > 100000000000 THEN 'Large Cap'
        WHEN market_cap BETWEEN 10000000000 AND 100000000000 THEN 'Mid Cap'
        ELSE 'Small Cap'
    END AS market_segment,
    COUNT(*) AS total_coins
FROM crypto_data
WHERE market_cap > 0
GROUP BY market_segment;

-- =====================================
-- 8. RANKING ANALYSIS
-- =====================================

SELECT 
    name,
    market_cap,
    RANK() OVER (ORDER BY market_cap DESC) AS rank
FROM crypto_data;

-- =====================================
-- 9. VOLUME CONTRIBUTION
-- =====================================

SELECT 
    name,
    volume,
    ROUND(volume * 100.0 / SUM(volume) OVER(), 2) AS volume_share_pct
FROM crypto_data
ORDER BY volume DESC
LIMIT 10;

-- =====================================
-- 10. TOP VS OTHERS
-- =====================================

SELECT 
    CASE 
        WHEN rank <= 5 THEN name
        ELSE 'Others'
    END AS category,
    SUM(market_cap) AS total_market_cap
FROM (
    SELECT 
        name,
        market_cap,
        RANK() OVER (ORDER BY market_cap DESC) AS rank
    FROM crypto_data
) t
GROUP BY category;

-- =====================================
-- 11. TIME ANALYSIS
-- =====================================

SELECT MAX(fetch_datetime) AS latest_time
FROM crypto_data;

SELECT *
FROM crypto_data
WHERE fetch_datetime = (SELECT MAX(fetch_datetime) FROM crypto_data);

SELECT COUNT(*) AS latest_snapshot_count
FROM crypto_data
WHERE fetch_datetime = (SELECT MAX(fetch_datetime) FROM crypto_data);

-- =====================================
-- 12. DATA QUALITY SCORE
-- =====================================

SELECT 
    COUNT(*) AS total_rows,
    COUNT(price) AS valid_price,
    COUNT(market_cap) AS valid_market_cap,
    COUNT(volume) AS valid_volume
FROM crypto_data;

-- =====================================
-- 13. HIGH ACTIVITY COINS
-- =====================================

SELECT 
    name,
    price,
    volume,
    market_cap,
    ROUND(volume * 1.0 / NULLIF(market_cap,0),4) AS activity_score
FROM crypto_data
ORDER BY activity_score DESC
LIMIT 10;

-- =====================================
-- 14. PRICE VS MARKET CAP
-- =====================================

SELECT 
    name,
    price,
    market_cap
FROM crypto_data
ORDER BY market_cap DESC;

-- =====================================
-- 15. NORMALIZED PRICE SCORE
-- =====================================

SELECT 
    name,
    price,
    (price - AVG(price) OVER()) / NULLIF(STDDEV(price) OVER(),0) AS z_score
FROM crypto_data;

-- =====================================
-- 16. FUTURE TREND ANALYSIS
-- =====================================

SELECT 
    name,
    DATE(fetch_datetime) AS fetch_date,
    AVG(price) AS avg_price
FROM crypto_data
GROUP BY name, DATE(fetch_datetime)
ORDER BY fetch_date;

SELECT 
    name,
    MAX(price) - MIN(price) AS price_change
FROM crypto_data
GROUP BY name
ORDER BY price_change DESC;

-- =====================================
-- 🔥 NEW (PRO LEVEL ADDITIONS)
-- =====================================

-- Latest Top 10 Coins (clean snapshot)
SELECT *
FROM crypto_dashboard
WHERE is_latest = 1
ORDER BY market_cap_rank
LIMIT 10;

-- Top Movers (based on price change)
SELECT 
    name,
    MAX(price) - MIN(price) AS price_change
FROM crypto_data
GROUP BY name
ORDER BY price_change DESC
LIMIT 10;

-- Daily Market Cap Trend
SELECT 
    DATE(fetch_datetime) AS date,
    SUM(market_cap) AS total_market_cap
FROM crypto_data
GROUP BY DATE(fetch_datetime)
ORDER BY date;