MERGE INTO GOLD.FCT_ORDERS target
USING (
  WITH enriched AS (
    SELECT o.order_id, o.customer_id, o.order_date, o.amount, o.currency,
           CASE o.currency WHEN 'INR' THEN o.amount WHEN 'USD' THEN o.amount * 83.0 END AS amount_inr,
           c.tier,
           FLOOR((CASE o.currency WHEN 'INR' THEN o.amount WHEN 'USD' THEN o.amount * 83.0 END) / 100)
             * CASE c.tier WHEN 'Gold' THEN 2 WHEN 'Silver' THEN 1 ELSE 0 END AS loyalty_points
    FROM SILVER.ORDERS_DEDUP o
    LEFT JOIN DIM.CUSTOMERS_SCD2 c
      ON o.customer_id = c.customer_id
     AND o.order_date::DATE >= c.effective_from
     AND (c.effective_to IS NULL OR o.order_date::DATE < c.effective_to)
  )
  SELECT *, SHA2(CONCAT_WS('|', order_id, customer_id, order_date::VARCHAR,
                            amount_inr::VARCHAR, tier, loyalty_points::VARCHAR), 256) AS row_hash
  FROM enriched
) source
ON target.order_id = source.order_id
WHEN MATCHED AND target.row_hash <> source.row_hash THEN UPDATE SET
  target.customer_id = source.customer_id,
  target.order_date = source.order_date,
  target.amount = source.amount,
  target.currency = source.currency,
  target.amount_inr = source.amount_inr,
  target.tier = source.tier,
  target.loyalty_points = source.loyalty_points,
  target.row_hash = source.row_hash,
  target.published_at = CURRENT_TIMESTAMP()
WHEN NOT MATCHED THEN INSERT
  (order_id, customer_id, order_date, amount, currency, amount_inr, tier,
   loyalty_points, row_hash, published_at)
VALUES
  (source.order_id, source.customer_id, source.order_date, source.amount,
   source.currency, source.amount_inr, source.tier, source.loyalty_points,
   source.row_hash, CURRENT_TIMESTAMP());