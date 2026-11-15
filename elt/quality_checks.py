from __future__ import annotations


QUALITY_CHECKS = {
    "raw_rows_have_payload": "SELECT COUNT_IF(raw_payload IS NULL) FROM bronze.orders_raw",
    "clean_rows_have_order_id": "SELECT COUNT_IF(order_id IS NULL) FROM silver.orders_clean",
    "dedup_has_unique_order_ids": "SELECT COUNT(*) - COUNT(DISTINCT order_id) FROM silver.orders_dedup",
    "gold_has_amount": "SELECT COUNT_IF(amount_inr IS NULL) FROM gold.fct_orders",
    "gold_points_nonnegative": "SELECT COUNT_IF(loyalty_points < 0) FROM gold.fct_orders",
    "gold_orders_not_future_dated": "SELECT COUNT_IF(order_date > CURRENT_DATE()) FROM gold.fct_orders",
}


def quality_checks(connection) -> list[tuple[str, int, str]]:
    results = []
    with connection.cursor() as cursor:
        for name, query in QUALITY_CHECKS.items():
            cursor.execute(query)
            count = int(cursor.fetchone()[0] or 0)
            status = "PASS" if count == 0 else "PROBLEM"
            results.append((name, count, status))
            print(f"{status}: {name} = {count}")
    return results