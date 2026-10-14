"""Optional Kafka adapter: bounded UTF-8 messages, JSON Lines output."""
import argparse
import json
import sys
from analyzer.core import MAX_CHARS, analyze


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--bootstrap-servers", default="localhost:9092")
    p.add_argument("--topic", required=True)
    p.add_argument("--group", default="string-analyzer")
    p.add_argument("--max-messages", type=int, default=100)
    p.add_argument("--timeout-ms", type=int, default=10000)
    a = p.parse_args()
    if a.max_messages < 1 or a.timeout_ms < 1:
        p.error("Message count and timeout must be positive.")
    try:
        from kafka import KafkaConsumer
    except ImportError:
        p.error("Install optional adapter: pip install kafka-python")
    consumer = KafkaConsumer(a.topic, bootstrap_servers=a.bootstrap_servers.split(","),
        group_id=a.group, enable_auto_commit=False, consumer_timeout_ms=a.timeout_ms)
    try:
        for index, message in enumerate(consumer, 1):
            try:
                if message.value is None: raise ValueError("Tombstone has no text")
                if len(message.value) > MAX_CHARS * 4: raise ValueError("Message exceeds size limit")
                report = {"topic": message.topic, "partition": message.partition,
                    "offset": message.offset, "analysis": analyze(message.value.decode("utf-8"))}
                print(json.dumps(report, ensure_ascii=False), flush=True)
            except (UnicodeError, ValueError) as error:
                print(f"Skipped offset {message.offset}: {error}", file=sys.stderr)
            if index >= a.max_messages: break
    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()


if __name__ == "__main__":
    main()
