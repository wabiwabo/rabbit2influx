from dotenv import load_dotenv
import os

class Config:
    """
    Configuration loader for RabbitMQ and InfluxDB.
    """
    def __init__(self):
        load_dotenv()
        # RabbitMQ settings
        self.rabbitmq_host = os.getenv("RABBITMQ_HOST")
        self.rabbitmq_queue = os.getenv("RABBITMQ_QUEUE")
        self.rabbitmq_username = os.getenv("RABBITMQ_USERNAME")
        self.rabbitmq_password = os.getenv("RABBITMQ_PASSWORD")
        self.rabbitmq_prefetch_count = int(os.getenv("RABBITMQ_PREFETCH_COUNT", 10))
        
        # InfluxDB settings
        self.influxdb_url = os.getenv("INFLUXDB_URL")
        self.influxdb_token = os.getenv("INFLUXDB_TOKEN")
        self.influxdb_org = os.getenv("INFLUXDB_ORG")
        self.influxdb_bucket = os.getenv("INFLUXDB_BUCKET")
        
        # Thread pool settings
        self.max_threads = int(os.getenv("THREAD_POOL_MAX_THREADS", 10))

        # Logging level
        self.log_level = os.getenv("LOG_LEVEL", "INFO").upper()

