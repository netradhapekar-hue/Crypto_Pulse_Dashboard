SELECT * 
FROM public_crypto_dashboard
WHERE id = 'zcash'
ORDER BY fetch_datetime;

SELECT DISTINCT fetch_date
FROM crypto_data;
-- CREATE TABLE IF NOT EXISTS crypto_data (
--     id TEXT,
--     symbol TEXT,
--     name TEXT,
--     price NUMERIC,
--     market_cap BIGINT,
--     volume BIGINT,
--     fetch_time TIMESTAMP,
--     fetch_date DATE
-- );
