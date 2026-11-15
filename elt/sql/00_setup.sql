CREATE SCHEMA IF NOT EXISTS BRONZE;
CREATE SCHEMA IF NOT EXISTS SILVER;
CREATE SCHEMA IF NOT EXISTS GOLD;
CREATE SCHEMA IF NOT EXISTS REF;
CREATE SCHEMA IF NOT EXISTS DIM;

CREATE TABLE IF NOT EXISTS BRONZE.ORDERS_RAW (
  raw_payload VARIANT NOT NULL,
  source_file VARCHAR,
  record_hash VARCHAR NOT NULL,
  loaded_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE IF NOT EXISTS SILVER.ORDERS_QUARANTINE (
  order_id VARCHAR,
  customer_id VARCHAR,
  order_date TIMESTAMP_NTZ,
  amount NUMBER(18, 2),
  currency VARCHAR,
  channel VARCHAR,
  updated_at TIMESTAMP_NTZ,
  reasons ARRAY,
  record_hash VARCHAR NOT NULL,
  quarantined_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE IF NOT EXISTS REF.MOCK_CRM_TIER_EVENTS (
  customer_id VARCHAR NOT NULL,
  customer_email VARCHAR,
  tier VARCHAR NOT NULL,
  effective_from DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS GOLD.FCT_ORDERS (
  order_id VARCHAR NOT NULL,
  customer_id VARCHAR,
  order_date TIMESTAMP_NTZ,
  amount NUMBER(18, 2),
  currency VARCHAR,
  amount_inr NUMBER(18, 2),
  tier VARCHAR,
  loyalty_points NUMBER(18, 0),
  row_hash VARCHAR NOT NULL,
  published_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

MERGE INTO REF.MOCK_CRM_TIER_EVENTS target
USING (
  SELECT column1 AS customer_id, column2 AS customer_email,
         column3 AS tier, TO_DATE(column4) AS effective_from
  FROM VALUES
    ('CUST-01', 'priya@example.com', 'Silver', '2026-01-01'),
    ('CUST-01', 'priya@example.com', 'Gold',   '2026-08-15'),
    ('CUST-02', 'arjun.k@yahoo.in', 'Silver', '2026-01-01'),
    ('CUST-02', 'arjun.k@yahoo.in', 'Gold',   '2026-08-25'),
    ('CUST-03', 'mira@example.com', 'Gold',   '2026-01-01')
) source
ON target.customer_id = source.customer_id
AND target.effective_from = source.effective_from
WHEN NOT MATCHED THEN INSERT (customer_id, customer_email, tier, effective_from)
VALUES (source.customer_id, source.customer_email, source.tier, source.effective_from);