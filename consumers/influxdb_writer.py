from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import logging

class InfluxDBWriter:
    """
    InfluxDB Writer for storing data points.
    """
    def __init__(self, config):
        """
        Initialize the InfluxDBWriter.

        Args:
            config: Configuration object containing InfluxDB settings.
        """
        self.config = config
        self.logger = logging.getLogger("InfluxDBWriter")

        # Define expected fields and their types
        self.expected_fields = {
            "channel_id": float,
            "custom_EVENT": float,
            "custom_battery_level": float,
            "custom_board_voltage": float,
            "custom_hw_mileage": float,
            "custom_raw_mileage": float,
            "position_altitude": float,
            "position_direction": float,
            "position_hdop": float,
            "position_latitude": float,
            "position_longitude": float,
            "position_satellites": float,
            "position_speed": float,
            "protocol_id": float,
        }
        
        # Enable debug mode based on config
        self.debug_mode = config.log_level == "DEBUG"


    def write(self, data):
        """
        Write data to InfluxDB.

        Args:
            data (dict): The data to write to InfluxDB. Expected format:
                {
                    "key": value,
                    "timestamp": <optional timestamp in seconds>
                }

        Logs:
            - Errors if the write operation fails.
            - Info-level logs for successfully written data.
        """
        if not isinstance(data, dict):
            self.logger.error(f"Invalid data format. Expected a dictionary, got {type(data).__name__}.")
            return

        try:
            with InfluxDBClient(
                url=self.config.influxdb_url,
                token=self.config.influxdb_token,
                org=self.config.influxdb_org,
            ) as client:
                write_api = client.write_api(write_options=SYNCHRONOUS)
                
                # Create a point for InfluxDB
                point = self.create_point(data)

                # Write the point to the specified bucket
                write_api.write(bucket=self.config.influxdb_bucket, record=point)
                self.logger.info(f"Successfully written data to InfluxDB: {data}")

        except Exception as e:
            self.logger.error(f"Failed to write data to InfluxDB. Error: {e}")

    def create_point(self, data):
        """
        Create an InfluxDB point from the input data.

        Args:
            data (dict): The data to convert into an InfluxDB point.

        Returns:
            Point: An InfluxDB point ready for writing.
        """
        point = Point("vehicle_data")

        for key, value in data.items():
            # Replace "." with "_" in field names to avoid conflicts
            formatted_key = key.replace(".", "_")

            if key in self.expected_fields:
                try:
                    # Validate field type
                    expected_type = expected_fields[key]
                    value = expected_type(value)
                except ValueError:
                    self.logger.warning(f"Skipping field {key} due to type mismatch: {value}, Expected type: {self.expected_fields.get(key)}")
                    continue

            if isinstance(value, (int, float)):
                point = point.field(formatted_key, float(value))
                if self.debug_mode:
                    self.logger.debug(f"Added field {formatted_key}: {value}, Expected type: {self.expected_fields.get(key)}")
                    self.logger.debug(f"Normalized {key}: {value} -> {float(value)}")
            elif isinstance(value, str):
                point = point.tag(formatted_key, value)
                if self.debug_mode:
                    self.logger.debug(f"Added field {formatted_key}: {value}, Expected type: {self.expected_fields.get(key)}")
        
        # Add a timestamp if available
        if "timestamp" in data:
            try:
                point = point.time(int(data["timestamp"]) * 10**9)  # Convert to nanoseconds
                if self.debug_mode:
                    self.logger.debug(f"Added timestamp: {data['timestamp']}")
            except ValueError as e:
                self.logger.warning(f"Invalid timestamp value: {data['timestamp']}. Skipping timestamp. Error: {e}")

        return point
