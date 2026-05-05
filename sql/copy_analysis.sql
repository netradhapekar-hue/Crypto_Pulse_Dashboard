-- ======================================
-- FINAL ANALYTICS LAYER
-- ======================================

DROP VIEW IF EXISTS crypto_dashboard;

CREATE VIEW crypto_dashboard AS

WITH latest_time AS (
    -- 9. TIME ANALYSIS → identifies latest snapshot timestamp
    SELECT MAX(fetch_datetime) AS max_time
    FROM crypto_dashboard_clean
),

latest_data AS (
    -- 9. TIME ANALYSIS → filters only latest data
    SELECT *
    FROM crypto_dashboard_clean
    WHERE fetch_datetime = (SELECT max_time FROM latest_time)
),

ranked_data AS (
    SELECT
        *,

        -- 1. MARKET LEADERS + 2. LOWEST PERFORMERS + 6. RANKING ANALYSIS
        RANK() OVER (ORDER BY market_cap DESC) AS market_cap_rank,

        -- 3. MARKET DOMINANCE
        ROUND((market_cap::numeric * 100.0 / SUM(market_cap) OVER()), 2) AS market_share_pct

    FROM latest_data
),

enhanced_data AS (
    SELECT 
        *,

        -- 4. LIQUIDITY ANALYSIS
        ROUND((volume::numeric / NULLIF(market_cap, 0)), 4) AS liquidity_ratio,

        -- 5. SEGMENTATION ANALYSIS (Price-based)
        CASE 
            WHEN price > 10000 THEN 'High Value'
            WHEN price BETWEEN 1000 AND 10000 THEN 'Mid Value'
            ELSE 'Low Value'
        END AS price_category,

        -- 5. SEGMENTATION ANALYSIS (Market Cap-based)
        CASE 
            WHEN market_cap > 100000000000 THEN 'Large Cap'
            WHEN market_cap BETWEEN 10000000000 AND 100000000000 THEN 'Mid Cap'
            ELSE 'Small Cap'
        END AS market_segment

    FROM ranked_data
),

trend_data AS (
    SELECT 
        id,

        -- 14. FUTURE TREND ANALYSIS + 16. TOP MOVERS
        MAX(price) - MIN(price) AS price_change

    FROM crypto_dashboard_clean
    GROUP BY id
)

SELECT 
    ed.*,                      -- Includes price, market_cap → 12. PRICE VS MARKET CAP
    td.price_change,           -- 14. FUTURE TREND + 16. TOP MOVERS

    -- 11. HIGH ACTIVITY COINS
    ROUND((ed.volume::numeric / NULLIF(ed.market_cap,0)), 4) AS activity_score,

    -- 13. NORMALIZED PRICE SCORE (Z-score)
    (ed.price - AVG(ed.price) OVER()) 
    / NULLIF(STDDEV(ed.price) OVER(),0) AS z_score

FROM enhanced_data ed
LEFT JOIN trend_data td
ON ed.id = td.id;