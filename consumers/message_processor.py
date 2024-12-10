import json
import logging

class MessageProcessor:
    """
    Processes RabbitMQ messages before storing in InfluxDB.
    """
    def __init__(self, influx_writer):
        """
        Initialize the MessageProcessor.

        Args:
            influx_writer: An instance responsible for writing data to InfluxDB.
        """
        self.influx_writer = influx_writer
        self.logger = logging.getLogger("MessageProcessor")

    def process(self, body):
        """
        Process a single RabbitMQ message.
 
        Args:
            body (bytes): The message body received from RabbitMQ.

        Logs:
            - Warnings for empty messages.
            - Errors for invalid JSON or unexpected issues.

        """
        if not body:
            self.logger.warning("Received empty message. Skipping processing.")
            return

        try:
            # Decode and parse the JSON message
            message = json.loads(body.decode("utf-8"))
            self.logger.info(f"Decoded message: {message}")

            # Validate the message structure (optional, based on your data requirements)
            if not isinstance(message, dict):
                self.logger.error(f"Invalid message format. Expected a dictionary, got: {type(message).__name__}")
                return

            # Process the message (write to InfluxDB)            
            self.influx_writer.write(message)
            self.logger.info(f"Successfully processed message: {message}")
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to decode JSON message: {body}. Error: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error processing message: {body}. Error: {e}")


