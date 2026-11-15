CREATE OR REPLACE TABLE SILVER.ORDERS_CHECKED AS
WITH normalized AS (
  SELECT
    COALESCE(raw_payload:"order_id"::VARCHAR, raw_payload:"orderId"::VARCHAR) AS order_id,
    COALESCE(raw_payload:"customer_id"::VARCHAR, raw_payload:"customerId"::VARCHAR) AS customer_id,
    TRY_TO_TIMESTAMP_NTZ(COALESCE(raw_payload:"order_date"::VARCHAR, raw_payload:"orderDate"::VARCHAR, raw_payload:"created_at"::VARCHAR)) AS order_date,
    TRY_TO_DECIMAL(COALESCE(raw_payload:"amount"::VARCHAR, raw_payload:"total"::VARCHAR), 18, 2) AS amount,
    UPPER(raw_payload:"currency"::VARCHAR) AS currency,
    COALESCE(raw_payload:"channel"::VARCHAR, raw_payload:"source"::VARCHAR) AS channel,
    TRY_TO_TIMESTAMP_NTZ(COALESCE(raw_payload:"updated_at"::VARCHAR, raw_payload:"updatedAt"::VARCHAR)) AS updated_at,
    record_hash,
    loaded_at
  FROM BRONZE.ORDERS_RAW
), checked AS (
  SELECT *, ARRAY_CONSTRUCT_COMPACT(
    IFF(order_id IS NULL, 'missing_order_id', NULL),
    IFF(customer_id IS NULL, 'missing_customer_id', NULL),
    IFF(order_date IS NULL, 'invalid_order_date', NULL),
    IFF(amount < 0, 'negative_amount', NULL),
    IFF(currency NOT IN ('INR', 'USD') OR currency IS NULL, 'unsupported_currency', NULL)
  ) AS reasons
  FROM normalized
)
SELECT * FROM checked;

CREATE OR REPLACE TABLE SILVER.ORDERS_CLEAN AS
SELECT order_id, customer_id, order_date, amount, currency, channel,
       updated_at, record_hash, loaded_at
FROM SILVER.ORDERS_CHECKED
WHERE ARRAY_SIZE(reasons) = 0;

MERGE INTO SILVER.ORDERS_QUARANTINE target
USING (
  SELECT order_id, customer_id, order_date, amount, currency, channel,
         updated_at, reasons, record_hash
  FROM SILVER.ORDERS_CHECKED
  WHERE ARRAY_SIZE(reasons) > 0
) source
ON target.record_hash = source.record_hash
WHEN NOT MATCHED THEN INSERT
  (order_id, customer_id, order_date, amount, currency, channel, updated_at, reasons, record_hash)
VALUES
  (source.order_id, source.customer_id, source.order_date, source.amount,
   source.currency, source.channel, source.updated_at, source.reasons, source.record_hash);