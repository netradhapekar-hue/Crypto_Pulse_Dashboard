-- Creating a table to import data from csv
CREATE TABLE IF NOT EXISTS crypto_data (
    id TEXT,
    symbol TEXT,
    name TEXT,
    price NUMERIC,
    market_cap BIGINT,
    volume BIGINT,
    fetch_time TIMESTAMP,
    fetch_date DATE
);

-- Checking if the data is loaded properly in the table 
SELECT COUNT(*) FROM crypto_data;

-- ==========================
-- 1. DATA VALIDATION CHECKS
-- ==========================

-- 1. Total rows
SELECT COUNT(*) AS total_rows FROM crypto_data;

-- 2. Check for null values
SELECT 
    COUNT(*) FILTER (WHERE price IS NULL) AS null_price,
    COUNT(*) FILTER (WHERE market_cap IS NULL) AS null_market_cap,
    COUNT(*) FILTER (WHERE volume IS NULL) AS null_volume
FROM crypto_data;

-- 3. Check duplicate IDs
SELECT id, COUNT(*)
FROM crypto_data
GROUP BY id
HAVING COUNT(*) > 1;


-- =====================================
-- 2. MARKET OVERVIEW KPIs
-- =====================================

SELECT 
    COUNT(*) AS total_coins,
    ROUND(AVG(price),2) AS avg_price,
    SUM(market_cap) AS total_market_cap,
    SUM(volume) AS total_volume,
    MAX(price) AS highest_price,
    MIN(price) AS lowest_price
FROM crypto_data;


-- =====================================
-- 3.  MARKET LEADERS
-- =====================================

-- 1. Top 10 by market cap
SELECT name, market_cap
FROM crypto_data
ORDER BY market_cap DESC
LIMIT 10;

-- 2. Top 10 by volume
SELECT name, volume
FROM crypto_data
ORDER BY volume DESC
LIMIT 10;

-- 3. Top 5 by price
SELECT name, price
FROM crypto_data
ORDER BY price DESC
LIMIT 10;


-- =====================================
-- 4. LOWEST PERFORMERS ANALYSIS
-- =====================================

-- 1. Bottom 10 Cryptos by Market Cap
SELECT name, market_cap
FROM crypto_data
ORDER BY market_cap ASC
LIMIT 10;

-- 2. Bottom 10 Cryptos by Trading Volume
SELECT name, volume
FROM crypto_data
ORDER BY volume ASC
LIMIT 10;

-- 3. Bottom 10 Cryptos by Price
SELECT name, price
FROM crypto_data
ORDER BY price ASC
LIMIT 10;

-- =====================================
-- 5. MARKET DOMINANCE
-- =====================================

SELECT 
    name,
    market_cap,
    ROUND(market_cap * 100.0 / SUM(market_cap) OVER(), 2) AS market_share_pct
FROM crypto_data
ORDER BY market_cap DESC
LIMIT 10;


-- =====================================
-- 6. LIQUIDITY ANALYSIS
-- =====================================

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

-- 1. Price Segmentation
SELECT 
    CASE 
        WHEN price > 10000 THEN 'High Value'
        WHEN price BETWEEN 1000 AND 10000 THEN 'Mid Value'
        ELSE 'Low Value'
    END AS price_category,
    COUNT(*) AS total_coins
FROM crypto_data
WHERE price IS NOT NULL 
  AND price > 0
GROUP BY price_category;

-- 2. Market Cap Segmentation
SELECT 
    CASE 
        WHEN market_cap > 100000000000 THEN 'Large Cap'
        WHEN market_cap BETWEEN 10000000000 AND 100000000000 THEN 'Mid Cap'
        ELSE 'Small Cap'
    END AS market_segment,
    COUNT(*) AS total_coins
FROM crypto_data
WHERE market_cap IS NOT NULL 
  AND market_cap > 0
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

-- 1. Latest snapshot timestamp
SELECT MAX(fetch_time) AS latest_time
FROM crypto_data;

-- 2. Data from latest snapshot ONLY (very important)
SELECT *
FROM crypto_data
WHERE fetch_time = (SELECT MAX(fetch_time) FROM crypto_data);

-- 3. Count of records in latest snapshot
SELECT COUNT(*) AS latest_snapshot_count
FROM crypto_data
WHERE fetch_time = (SELECT MAX(fetch_time) FROM crypto_data);


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
-- 13. HIGH VOLATILITY / POTENTIAL MOVERS
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
-- 14. PRICE VS MARKET CAP RELATION
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

-- 1. Price trend over time
SELECT 
    name,
    fetch_date,
    AVG(price) AS avg_price
FROM crypto_data
GROUP BY name, fetch_date
ORDER BY fetch_date;

-- 2. Price change detection
SELECT 
    name,
    MAX(price) - MIN(price) AS price_change
FROM crypto_data
GROUP BY name
ORDER BY price_change DESC;



-- ==============================
-- MASTER VIEW
-- ==============================

-- =====================================
-- FINAL DATASET FOR DASHBOARD
-- =====================================

CREATE OR REPLACE VIEW crypto_dashboard AS
SELECT 
    name,
    symbol,
    price,
    market_cap,
    volume,

    -- Rankings
    RANK() OVER (ORDER BY market_cap DESC) AS market_cap_rank,

    -- Market share
    ROUND(market_cap * 100.0 / SUM(market_cap) OVER(), 2) AS market_share_pct,

    -- Liquidity
    ROUND(volume * 1.0 / NULLIF(market_cap, 0), 4) AS liquidity_ratio,

    -- Segments
    CASE 
        WHEN price > 10000 THEN 'High Value'
        WHEN price BETWEEN 1000 AND 10000 THEN 'Mid Value'
        ELSE 'Low Value'
    END AS price_category,

    CASE 
        WHEN market_cap > 100000000000 THEN 'Large Cap'
        WHEN market_cap BETWEEN 10000000000 AND 100000000000 THEN 'Mid Cap'
        ELSE 'Small Cap'
    END AS market_segment,

    fetch_time,
    fetch_date

FROM crypto_data
WHERE fetch_time = (SELECT MAX(fetch_time) FROM crypto_data);