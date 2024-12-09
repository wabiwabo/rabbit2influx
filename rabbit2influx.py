import pika
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import json
import logging
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
import os

# Load configuration from .env
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("RabbitToInflux")

# Configuration from .env
RABBITMQ_CONFIG = {
    "host": os.getenv("RABBITMQ_HOST"),
    "queue": os.getenv("RABBITMQ_QUEUE"),
    "username": os.getenv("RABBITMQ_USERNAME"),
    "password": os.getenv("RABBITMQ_PASSWORD"),
    "prefetch_count": int(os.getenv("RABBITMQ_PREFETCH_COUNT", 10))
}

INFLUXDB_CONFIG = {
    "url": os.getenv("INFLUXDB_URL"),
    "token": os.getenv("INFLUXDB_TOKEN"),
    "org": os.getenv("INFLUXDB_ORG"),
    "bucket": os.getenv("INFLUXDB_BUCKET")
}

THREAD_POOL_CONFIG = {
    "max_threads": int(os.getenv("THREAD_POOL_MAX_THREADS", 10))
}


# RabbitMQ Consumer Class
class RabbitMQConsumer:
    def __init__(self, config, callback):
        self.config = config
        self.callback = callback
        self.connection = None
        self.channel = None

    def connect(self):
        credentials = pika.PlainCredentials(
            self.config["username"], self.config["password"]
        )
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.config["host"], credentials=credentials)
        )
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.config["queue"], durable=True)
        self.channel.basic_qos(prefetch_count=self.config["prefetch_count"])
        logger.info("Connected to RabbitMQ and ready to consume messages.")

    def start_consuming(self):
        self.channel.basic_consume(
            queue=self.config["queue"], on_message_callback=self.callback, auto_ack=True
        )
        logger.info("Started consuming messages.")
        self.channel.start_consuming()

    def close(self):
        if self.connection:
            self.connection.close()
            logger.info("Closed RabbitMQ connection.")


# InfluxDB Writer Class
class InfluxDBWriter:
    def __init__(self, config):
        self.config = config

    def write(self, message):
        try:
            with InfluxDBClient(
                url=self.config["url"],
                token=self.config["token"],
                org=self.config["org"],
            ) as client:
                write_api = client.write_api(write_options=SYNCHRONOUS)

                point = Point("vehicle_data").tag(
                    "device_name", message.get("device.name", "unknown")
                ).tag("ident", message.get("ident", "unknown"))

                for key, value in message.items():
                    if isinstance(value, (int, float)):
                        point = point.field(key.replace(".", "_"), value)

                if "timestamp" in message:
                    point = point.time(int(message["timestamp"]) * 10**9)

                write_api.write(bucket=self.config["bucket"], record=point)
                logger.info(f"Message written to InfluxDB: {message}")

        except Exception as e:
            logger.error(f"Failed to write message to InfluxDB: {e}")


def process_message(body):
    """
    Process a single RabbitMQ message and write it to InfluxDB.
    """
    if not body:
        logger.warning("Received an empty message. Skipping...")
        return

    try:
        message = json.loads(body.decode())  # Parse JSON
        logger.info(f"Processing message: {message}")
        influx_writer.write(message)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON message: {body.decode()}. Error: {e}")
    except Exception as e:
        logger.error(f"Failed to process message: {e}")


if __name__ == "__main__":
    influx_writer = InfluxDBWriter(INFLUXDB_CONFIG)
    executor = ThreadPoolExecutor(max_workers=THREAD_POOL_CONFIG["max_threads"])

    def thread_safe_callback(ch, method, properties, body):
        executor.submit(process_message, body)

    consumer = RabbitMQConsumer(RABBITMQ_CONFIG, thread_safe_callback)
    try:
        consumer.connect()
        consumer.start_consuming()
    except KeyboardInterrupt:
        logger.info("Stopping consumer due to keyboard interrupt.")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
    finally:
        consumer.close()

