from __future__ import annotations

MOCK_ORDERS = [
    {"order_id": "ORD-1001", "customer_id": "CUST-01", "created_at": "2026-08-01T10:00:00", "total": 885, "currency": "INR", "source": "website", "updated_at": "2026-08-01T10:05:00"},
    {"order_id": "ORD-1002", "customer_id": "CUST-02", "created_at": "2026-08-20T11:00:00", "total": 2000, "currency": "INR", "source": "website", "updated_at": "2026-08-20T11:05:00"},
    {"order_id": "ORD-1003", "customer_id": "CUST-03", "created_at": "2026-08-05T12:00:00", "currency": "INR", "source": "website", "updated_at": "2026-08-05T12:05:00"},
    {"order_id": "ORD-1004", "customer_id": "CUST-03", "created_at": "2026-08-06T12:00:00", "total": -1, "currency": "INR", "source": "website", "updated_at": "2026-08-06T12:05:00"},
    {"order_id": "ORD-1005", "customer_id": "CUST-01", "created_at": "2026-08-20T13:00:00", "total": 2800, "currency": "INR", "source": "website", "updated_at": "2026-08-20T13:05:00"},
    {"order_id": "ORD-1006", "created_at": "2026-08-21T14:00:00", "total": 500, "currency": "GBP", "source": "website", "updated_at": "2026-08-21T14:05:00"},
    {"orderId": "ORD-1003", "customerId": "CUST-03", "orderDate": "2026-08-05T12:00:00", "amount": 2100, "currency": "INR", "channel": "mobile", "updatedAt": "2026-08-05T12:10:00"},
    {"orderId": "ORD-1005", "customerId": "CUST-01", "orderDate": "2026-08-20T13:00:00", "amount": 2800, "currency": "INR", "channel": "mobile", "updatedAt": "2026-08-20T13:10:00"},
]

MOCK_CRM_TIER_EVENTS = [
    {"customer_id": "CUST-01", "customer_email": "priya@example.com", "tier": "Silver", "effective_from": "2026-01-01"},
    {"customer_id": "CUST-01", "customer_email": "priya@example.com", "tier": "Gold", "effective_from": "2026-08-15"},
    {"customer_id": "CUST-02", "customer_email": "arjun.k@yahoo.in", "tier": "Silver", "effective_from": "2026-01-01"},
    {"customer_id": "CUST-03", "customer_email": "mira@example.com", "tier": "Gold", "effective_from": "2026-01-01"},
]