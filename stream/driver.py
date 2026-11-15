from __future__ import annotations

import argparse
import json
import os

from stream.routing import topic_matches


def consume(name: str, pattern: str) -> None:
    import pika

    broker_url = os.environ.get("RABBITMQ_URL")
    if not broker_url:
        raise RuntimeError("Set RABBITMQ_URL before starting a driver")
    connection = pika.BlockingConnection(pika.URLParameters(broker_url))
    channel = connection.channel()
    exchange = "rapido-dispatch"
    channel.exchange_declare(exchange=exchange, exchange_type="topic", durable=True)
    result = channel.queue_declare(queue="", exclusive=True, auto_delete=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange=exchange, queue=queue_name, routing_key=pattern)
    channel.basic_qos(prefetch_count=1)
    print(f"driver={name} pattern={pattern} queue={queue_name}", flush=True)

    def on_message(ch, method, properties, body):
        try:
            message = json.loads(body)
            if not isinstance(message, dict) or not message.get("zone"):
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                print(f"NACK discarded key={method.routing_key} body={body!r}", flush=True)
                return
            print(
                f"driver={name} key={method.routing_key} order={message}", flush=True
            )
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except (json.JSONDecodeError, UnicodeDecodeError):
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            print(f"NACK invalid-json key={method.routing_key}", flush=True)

    channel.basic_consume(queue=queue_name, on_message_callback=on_message)
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    finally:
        connection.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("name")
    parser.add_argument("pattern")
    args = parser.parse_args()
    consume(args.name, args.pattern)


if __name__ == "__main__":
    main()