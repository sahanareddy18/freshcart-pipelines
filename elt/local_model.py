from __future__ import annotations

from datetime import datetime
from typing import Any


def _value(record: dict[str, Any], *names: str) -> Any:
    for name in names:
        value = record.get(name)
        if value is not None:
            return value
    return None


def normalize(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "order_id": _value(record, "order_id", "orderId"),
        "customer_id": _value(record, "customer_id", "customerId"),
        "order_date": _value(record, "order_date", "orderDate", "created_at"),
        "amount": _value(record, "amount", "total"),
        "currency": record.get("currency"),
        "channel": _value(record, "channel", "source"),
        "updated_at": _value(record, "updated_at", "updatedAt"),
        "raw": record,
    }


def clean_records(
    records: list[dict[str, Any]], *, validate_currency: bool = True
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    clean: list[dict[str, Any]] = []
    quarantine: list[dict[str, Any]] = []
    for raw in records:
        row = normalize(raw)
        reasons = []
        if not row["order_id"]:
            reasons.append("missing_order_id")
        if not row["customer_id"]:
            reasons.append("missing_customer_id")
        if row["amount"] is not None and float(row["amount"]) < 0:
            reasons.append("negative_amount")
        if validate_currency and row["currency"] not in {"INR", "USD"}:
            reasons.append("unsupported_currency")
        row["reasons"] = reasons
        (quarantine if reasons else clean).append(row)
    return clean, quarantine


def deduplicate(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for row in rows:
        order_id = row["order_id"]
        current = latest.get(order_id)
        rank = (
            datetime.fromisoformat(str(row["updated_at"])).timestamp(),
            row["amount"] is not None,
        )
        current_rank = (
            datetime.fromisoformat(str(current["updated_at"])).timestamp(),
            current["amount"] is not None,
        ) if current else None
        if current is None or rank > current_rank:
            latest[order_id] = row
    return list(latest.values())


def to_gold_amount(row: dict[str, Any], usd_to_inr: float = 83.0) -> float | None:
    if row["amount"] is None:
        return None
    amount = float(row["amount"])
    return amount if row["currency"] == "INR" else amount * usd_to_inr


def loyalty_points(amount_inr: float, tier: str) -> int:
    multiplier = {"Gold": 2, "Silver": 1}.get(tier, 0)
    return int(amount_inr // 100) * multiplier