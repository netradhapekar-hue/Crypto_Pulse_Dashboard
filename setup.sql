-- Create table
CREATE TABLE crypto_data (
    id TEXT,
    symbol TEXT,
    name TEXT,
    price NUMERIC,
    market_cap BIGINT,
    volume BIGINT,
    fetch_datetime TIMESTAMP
);

-- Create view
CREATE OR REPLACE VIEW crypto_dashboard AS
WITH latest_time AS (
    SELECT MAX(fetch_datetime) AS max_time
    FROM crypto_data
),

latest_data AS (
    SELECT *
    FROM crypto_data
    WHERE fetch_datetime = (SELECT max_time FROM latest_time)
),

ranked_latest AS (
    SELECT
        id,
        RANK() OVER (ORDER BY market_cap DESC) AS market_cap_rank,
        ROUND(market_cap * 100.0 / SUM(market_cap) OVER(), 2) AS market_share_pct
    FROM latest_data
)

SELECT 
    cd.*,
    rl.market_cap_rank,
    rl.market_share_pct,

    ROUND(cd.volume * 1.0 / NULLIF(cd.market_cap, 0), 4) AS liquidity_ratio,

    CASE 
        WHEN cd.price > 10000 THEN 'High Value'
        WHEN cd.price BETWEEN 1000 AND 10000 THEN 'Mid Value'
        ELSE 'Low Value'
    END AS price_category,

    CASE 
        WHEN cd.market_cap > 100000000000 THEN 'Large Cap'
        WHEN cd.market_cap BETWEEN 10000000000 AND 100000000000 THEN 'Mid Cap'
        ELSE 'Small Cap'
    END AS market_segment,

    CASE 
        WHEN cd.fetch_datetime = (SELECT max_time FROM latest_time) THEN 1
        ELSE 0
    END AS is_latest

FROM crypto_data cd
LEFT JOIN ranked_latest rl
ON cd.id = rl.id;