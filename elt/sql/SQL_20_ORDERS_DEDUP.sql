CREATE OR REPLACE TABLE SILVER.ORDERS_DEDUP AS
SELECT order_id, customer_id, order_date, amount, currency, channel,
       updated_at, record_hash, loaded_at
FROM SILVER.ORDERS_CLEAN
QUALIFY ROW_NUMBER() OVER (
  PARTITION BY order_id
  ORDER BY updated_at DESC, IFF(amount IS NOT NULL, 1, 0) DESC, loaded_at DESC
) = 1;