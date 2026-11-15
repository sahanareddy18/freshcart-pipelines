from elt.local_model import clean_records, deduplicate, loyalty_points, to_gold_amount
from elt.sample_orders import MOCK_ORDERS


def test_mock_batch_has_expected_row_flow_and_revenue():
    clean, quarantine = clean_records(MOCK_ORDERS)
    orders = deduplicate(clean)

    assert len(MOCK_ORDERS) == 8
    assert len(clean) == 6
    assert len(quarantine) == 2
    assert len(orders) == 4
    assert sum(to_gold_amount(row) for row in orders) == 7785


def test_latest_mobile_order_wins_and_has_amount():
    clean, _ = clean_records(MOCK_ORDERS)
    order = next(row for row in deduplicate(clean) if row["order_id"] == "ORD-1003")

    assert order["channel"] == "mobile"
    assert order["amount"] == 2100


def test_fixture_matches_baseline_gold_revenue_and_points():
    clean, _ = clean_records(MOCK_ORDERS)
    orders = deduplicate(clean)
    tiers = {
        "ORD-1001": "Silver",
        "ORD-1002": "Silver",
        "ORD-1003": "Gold",
        "ORD-1005": "Gold",
    }
    points = sum(
        loyalty_points(to_gold_amount(row), tiers[row["order_id"]])
        for row in orders
    )

    assert sum(to_gold_amount(row) for row in orders) == 7785
    assert points == 126


def test_currency_rule_adds_quarantine_reason_without_new_row():
    before_clean, before_quarantine = clean_records(MOCK_ORDERS, validate_currency=False)
    after_clean, after_quarantine = clean_records(MOCK_ORDERS, validate_currency=True)
    before_1006 = next(row for row in before_quarantine if row["order_id"] == "ORD-1006")
    after_1006 = next(row for row in after_quarantine if row["order_id"] == "ORD-1006")

    assert "unsupported_currency" not in before_1006["reasons"]
    assert "unsupported_currency" in after_1006["reasons"]
    assert len(before_quarantine) == len(after_quarantine) == 2
    assert len(before_clean) == len(after_clean) == 6