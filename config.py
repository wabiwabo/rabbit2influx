from dotenv import load_dotenv
import os
import logging


class Config:
    """
    Configuration loader for RabbitMQ and InfluxDB.
    """
    def __init__(self):
        load_dotenv()

        # RabbitMQ settings
        self.rabbitmq_host = self.get_env_var("RABBITMQ_HOST", required=True)
        self.rabbitmq_vhost = self.get_env_var("RABBITMQ_VHOST", required=True)
        self.rabbitmq_queue = self.get_env_var("RABBITMQ_QUEUE", required=True)
        self.rabbitmq_username = self.get_env_var("RABBITMQ_USERNAME", required=True)
        self.rabbitmq_password = self.get_env_var("RABBITMQ_PASSWORD", required=True)
        self.rabbitmq_prefetch_count = self.get_env_var("RABBITMQ_PREFETCH_COUNT", default=10, cast=int)

        # InfluxDB settings
        self.influxdb_url = self.get_env_var("INFLUXDB_URL", required=True)
        self.influxdb_token = self.get_env_var("INFLUXDB_TOKEN", required=True)
        self.influxdb_org = self.get_env_var("INFLUXDB_ORG", required=True)
        self.influxdb_bucket = self.get_env_var("INFLUXDB_BUCKET", required=True)

        # Thread pool settings
        self.max_threads = self.get_env_var("THREAD_POOL_MAX_THREADS", default=10, cast=int)

        # Logging level
        self.log_level = self.get_env_var("LOG_LEVEL", default="INFO").upper()

        # Configure logging
        self.configure_logging()

    def get_env_var(self, key, required=False, default=None, cast=str):
        """
        Helper method to retrieve environment variables with optional casting and default values.
        
        Args:
            key (str): The environment variable key.
            required (bool): Whether the variable is required. Default is False.
            default: The default value if the variable is not set. Default is None.
            cast (type): Type to cast the environment variable value to. Default is str.

        Returns:
            The value of the environment variable, cast to the specified type.

        Raises:
            ValueError: If a required variable is missing.
        """
        value = os.getenv(key, default)
        if required and value is None:
            raise ValueError(f"Missing required environment variable: {key}")
        try:
            return cast(value)
        except (TypeError, ValueError) as e:
            raise ValueError(f"Invalid value for environment variable {key}: {value}. Expected {cast.__name__}") from e

    def configure_logging(self):
        """
        Configure the application logging settings.
        """
        logging.basicConfig(
            level=getattr(logging, self.log_level, logging.INFO),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        logging.getLogger("pika").setLevel(logging.WARNING)  # Suppress verbose pika logs
