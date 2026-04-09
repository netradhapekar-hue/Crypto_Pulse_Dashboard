SELECT * 
FROM public_crypto_dashboard
WHERE id = 'zcash'
ORDER BY fetch_datetime;

SELECT DISTINCT fetch_date
FROM crypto_data;