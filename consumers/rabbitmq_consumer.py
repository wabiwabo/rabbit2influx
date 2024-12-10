import pika
import logging

class RabbitMQConsumer:
    """
    RabbitMQ Consumer for reading messages.
    """
    def __init__(self, config, callback):
        self.config = config
        self.callback = callback
        self.connection = None
        self.channel = None
        self.logger = logging.getLogger("RabbitMQConsumer")

    def connect(self):
        """
        Establish a connection to RabbitMQ.
        """
        self.logger.info("Connecting to RabbitMQ...")
        credentials = pika.PlainCredentials(
            self.config.rabbitmq_username, self.config.rabbitmq_password
        )
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.config.rabbitmq_host, virtual_host=self.config.rabbitmq_vhost, credentials=credentials)
        )
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.config.rabbitmq_queue, durable=True)
        self.channel.basic_qos(prefetch_count=self.config.rabbitmq_prefetch_count)
        self.logger.info("Connected to RabbitMQ.")

    def start_consuming(self):
        """
        Start consuming messages from RabbitMQ.
        """
        self.logger.info("Starting to consume messages...")
        self.channel.basic_consume(
            queue=self.config.rabbitmq_queue, on_message_callback=self.callback, auto_ack=True
        )
        self.channel.start_consuming()

    def close(self):
        """
        Close the RabbitMQ connection.
        """
        if self.connection:
            self.connection.close()
            self.logger.info("RabbitMQ connection closed.")

