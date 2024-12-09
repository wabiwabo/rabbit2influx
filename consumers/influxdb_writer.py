from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import logging

class InfluxDBWriter:
    """
    InfluxDB Writer for storing data points.
    """
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger("InfluxDBWriter")

    def write(self, data):
        """
        Write data to InfluxDB.
        """
        try:
            with InfluxDBClient(
                url=self.config.influxdb_url,
                token=self.config.influxdb_token,
                org=self.config.influxdb_org,
            ) as client:
                write_api = client.write_api(write_options=SYNCHRONOUS)
                
                point = Point("vehicle_data")
                for key, value in data.items():
                    if isinstance(value, (int, float)):
                        point = point.field(key.replace(".", "_"), value)
                if "timestamp" in data:
                    point = point.time(int(data["timestamp"]) * 10**9)
                
                write_api.write(bucket=self.config.influxdb_bucket, record=point)
                self.logger.info(f"Data written to InfluxDB: {data}")
        except Exception as e:
            self.logger.error(f"Failed to write data to InfluxDB: {e}")

