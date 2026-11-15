from __future__ import annotations

import argparse
import json
import os
import time

from elt.sample_orders import MOCK_ORDERS


def publish_orders(interval: float, repeat: int) -> None:
    import pika

    broker_url = os.environ.get("RABBITMQ_URL")
    if not broker_url:
        raise RuntimeError("Set RABBITMQ_URL before publishing FreshCart events")
    connection = pika.BlockingConnection(pika.URLParameters(broker_url))
    channel = connection.channel()
    exchange = "freshcart-orders"
    channel.exchange_declare(exchange=exchange, exchange_type="topic", durable=True)
    try:
        for batch in range(repeat):
            for record in MOCK_ORDERS:
                channel.basic_publish(
                    exchange=exchange,
                    routing_key="orders.created",
                    body=json.dumps(record),
                    properties=pika.BasicProperties(
                        content_type="application/json", delivery_mode=2
                    ),
                )
                print(f"published order={record.get('order_id', record.get('orderId'))}")
                time.sleep(interval)
    finally:
        connection.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--interval", type=float, default=1)
    parser.add_argument("--repeat", type=int, default=1)
    args = parser.parse_args()
    publish_orders(args.interval, args.repeat)


if __name__ == "__main__":
    main()