from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

from elt.snowflake_io import connect_from_env, execute_transform_sql, load_file, write_landing

SQL_STEPS = (
    "00_setup.sql",
    "SQL_10_ORDERS_CLEAN.sql",
    "SQL_20_ORDERS_DEDUP.sql",
    "SQL_30_CUSTOMERS_SCD2.sql",
    "SQL_40_GOLD_MERGE.sql",
)


def collect_orders(duration: int, pattern: str) -> list[dict]:
    import pika

    broker_url = os.environ.get("RABBITMQ_URL")
    if not broker_url:
        raise RuntimeError("Set RABBITMQ_URL before starting the landing consumer")
    connection = pika.BlockingConnection(pika.URLParameters(broker_url))
    channel = connection.channel()
    exchange = "freshcart-orders"
    channel.exchange_declare(exchange=exchange, exchange_type="topic", durable=True)
    queue_name = channel.queue_declare(queue="", exclusive=True, auto_delete=True).method.queue
    channel.queue_bind(exchange=exchange, queue=queue_name, routing_key=pattern)
    messages: list[dict] = []

    def on_message(ch, method, properties, body):
        try:
            record = json.loads(body)
            if not isinstance(record, dict) or not record.get("order_id", record.get("orderId")):
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                print(f"NACK invalid order key={method.routing_key}", flush=True)
                return
            messages.append(record)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            print(f"ACK landed order={record.get('order_id', record.get('orderId'))}", flush=True)
        except (json.JSONDecodeError, UnicodeDecodeError):
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    channel.basic_consume(queue=queue_name, on_message_callback=on_message)
    print(f"Collecting for {duration}s on {exchange} with pattern {pattern}", flush=True)
    deadline = time.monotonic() + duration
    try:
        while time.monotonic() < deadline:
            connection.process_data_events(time_limit=1)
    finally:
        connection.close()
    return messages


def apply_batch(path: Path) -> tuple[object, object]:
    from pathlib import Path as LocalPath

    root = LocalPath(__file__).resolve().parents[1]
    connection = connect_from_env()
    try:
        load_file(connection, path)
        for sql_name in SQL_STEPS:
            execute_transform_sql(connection, root / "elt" / "sql" / sql_name)
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*), SUM(amount_inr) FROM gold.fct_orders")
            before_replay = cursor.fetchone()

        for sql_name in SQL_STEPS[1:]:
            execute_transform_sql(connection, root / "elt" / "sql" / sql_name)
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*), SUM(amount_inr) FROM gold.fct_orders")
            after_replay = cursor.fetchone()
        print(f"gold before replay: rows={before_replay[0]}, revenue={before_replay[1]}")
        print(f"gold after replay:  rows={after_replay[0]}, revenue={after_replay[1]}")
        return before_replay, after_replay
    finally:
        connection.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration", type=int, default=60)
    parser.add_argument("--pattern", default="orders.#")
    parser.add_argument("--landing-dir", default="landing/stream")
    args = parser.parse_args()
    records = collect_orders(args.duration, args.pattern)
    if not records:
        print("No valid order messages received; nothing loaded")
        return
    path = write_landing(records, args.landing_dir)
    print(f"Wrote {len(records)} messages to {path}")
    apply_batch(path)


if __name__ == "__main__":
    main()