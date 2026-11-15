CREATE OR REPLACE TABLE DIM.CUSTOMERS_SCD2 AS
WITH ordered_events AS (
  SELECT customer_id, customer_email, tier, effective_from,
         LEAD(effective_from) OVER (
           PARTITION BY customer_id ORDER BY effective_from
         ) AS next_effective_from
  FROM REF.MOCK_CRM_TIER_EVENTS
)
SELECT customer_id, customer_email, tier, effective_from,
       next_effective_from AS effective_to,
       next_effective_from IS NULL AS is_current
FROM ordered_events;