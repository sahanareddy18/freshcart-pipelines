from __future__ import annotations

import argparse
import json
import os
import random
import time
import uuid
from datetime import datetime, timezone

from stream.routing import topic_matches

CITIES = {"bangalore": ["koramangala", "indiranagar", "whitefield"], "chennai": ["tnagar", "whitefield"]}
ORDER_TYPES = ("ride", "food")


def make_request(index: int, routing_key: str | None = None) -> tuple[str, dict]:
    if routing_key:
        city, zone, request_type = (routing_key.split(".") + [None] * 3)[:3]
    else:
        city = random.choice(tuple(CITIES))
        zone = random.choice(CITIES[city])
        request_type = random.choice(ORDER_TYPES)
        routing_key = f"{city}.{zone}.{request_type}"

    payload = {
        "id": str(uuid.uuid4()),
        "city": city,
        "zone": zone,
        "type": request_type,
        "ts": datetime.now(timezone.utc).isoformat(),
    }
    if index % 10 == 0:
        payload.pop("zone")
    return routing_key, payload


def publish_messages(duration: int, interval: float, routing_key: str | None = None) -> None:
    import pika

    broker_url = os.environ.get("RABBITMQ_URL")
    if not broker_url:
        raise RuntimeError("Set RABBITMQ_URL before starting the dispatcher")
    connection = pika.BlockingConnection(pika.URLParameters(broker_url))
    channel = connection.channel()
    exchange = "rapido-dispatch"
    channel.exchange_declare(exchange=exchange, exchange_type="topic", durable=True)
    deadline = time.monotonic() + duration
    index = 0
    try:
        while time.monotonic() < deadline:
            index += 1
            key, payload = make_request(index, routing_key)
            channel.basic_publish(
                exchange=exchange,
                routing_key=key,
                body=json.dumps(payload),
                properties=pika.BasicProperties(
                    content_type="application/json", delivery_mode=2
                ),
            )
            status = "malformed" if "zone" not in payload else "published"
            print(f"{status} id={payload['id']} key={key} payload={payload}", flush=True)
            time.sleep(interval)
    finally:
        connection.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration", type=int, default=120)
    parser.add_argument("--interval", type=float, default=2)
    parser.add_argument("--routing-key", help="Use one fixed key for a routing demonstration")
    args = parser.parse_args()
    publish_messages(args.duration, args.interval, args.routing_key)


if __name__ == "__main__":
    main()