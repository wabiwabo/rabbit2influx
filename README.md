Here’s a **README.md** file for your project, explaining the features and functionality of the RabbitMQ-to-InfluxDB integration:

---

# **RabbitMQ to InfluxDB Integration**

This project implements a **RabbitMQ consumer** that processes messages and writes structured data to **InfluxDB**. It is designed to handle high message traffic efficiently using a multi-threaded architecture and offers flexibility through environment-based configurations.

---

## **Features**

### **1. RabbitMQ Integration**
- **Consume Messages**: Reads messages from a specified RabbitMQ queue.
- **Prefetch Control**: Limits the number of unacknowledged messages with configurable `prefetch_count`.
- **Reliable Connection**: Automatically reconnects to RabbitMQ if the connection is dropped.

### **2. InfluxDB Integration**
- **Write Data**: Stores parsed messages as structured time-series data in InfluxDB.
- **Customizable Measurement**: Maps message fields to InfluxDB tags and fields.
- **Support for Timestamps**: Handles custom timestamps in nanoseconds for precise time-series data.

### **3. Environment-Based Configuration**
- **Flexible Settings**: Configure RabbitMQ and InfluxDB credentials, queue names, and thread pool size using a `.env` file.
- **Secure**: Excludes sensitive credentials from the codebase.

### **4. High-Performance Processing**
- **Multi-Threaded Consumer**: Processes multiple messages concurrently using Python's `ThreadPoolExecutor`.
- **Scalable Design**: Easily configurable to handle high traffic by adjusting the thread pool size.

### **5. Robust Logging**
- **Structured Logs**: Logs connection details, message processing status, and errors.
- **Debugging Support**: Configurable log levels (`DEBUG`, `INFO`, `ERROR`) for development and production.

---

## **Architecture Overview**

The application follows a modular design pattern:
1. **RabbitMQ Consumer**:
   - Establishes a connection to RabbitMQ.
   - Reads messages from a specified queue.
   - Passes messages to the processing pipeline.

2. **Message Processor**:
   - Parses incoming JSON messages.
   - Validates data and handles errors gracefully.
   - Sends structured data to the InfluxDB writer.

3. **InfluxDB Writer**:
   - Maps data fields to InfluxDB measurements, tags, and fields.
   - Writes time-series data to a specified bucket.
   - Handles connection retries for transient failures.

4. **Thread Pool**:
   - Concurrently processes messages for improved performance.

---

## **Setup and Installation**

### **1. Clone the Repository**
```bash
git clone https://github.com/<your-username>/rabbitmq-to-influxdb.git
cd rabbitmq-to-influxdb
```

### **2. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **3. Set Up Configuration**
Create a `.env` file in the root directory with the following content:
```env
# RabbitMQ Configuration
RABBITMQ_HOST=localhost
RABBITMQ_QUEUE=your_queue_name
RABBITMQ_USERNAME=guest
RABBITMQ_PASSWORD=guest
RABBITMQ_PREFETCH_COUNT=10

# InfluxDB Configuration
INFLUXDB_URL=http://localhost:8086
INFLUXDB_TOKEN=your_influxdb_token
INFLUXDB_ORG=your_org
INFLUXDB_BUCKET=your_bucket

# Thread Pool Configuration
THREAD_POOL_MAX_THREADS=10

# Logging Level
LOG_LEVEL=INFO
```

### **4. Run the Application**
```bash
python main.py
```

---

## **How It Works**

### **Message Flow**
1. RabbitMQ publishes messages in JSON format to the specified queue.
2. The consumer reads these messages and passes them to the message processor.
3. The processor:
   - Parses the JSON payload.
   - Extracts relevant fields for storage.
   - Sends the structured data to the InfluxDB writer.
4. The InfluxDB writer maps the data to a measurement and writes it to InfluxDB.

### **Example Message**
```json
{
    "device.name": "sensor1",
    "timestamp": 1672531200,
    "position.latitude": -6.9175,
    "position.longitude": 107.6191,
    "temperature": 25.3
}
```

### **InfluxDB Mapping**
- **Measurement**: `vehicle_data`
- **Tags**:
  - `device_name`: `sensor1`
- **Fields**:
  - `position_latitude`: `-6.9175`
  - `position_longitude`: `107.6191`
  - `temperature`: `25.3`
- **Timestamp**: `1672531200` (converted to nanoseconds)

---

## **Development and Testing**

### **Unit Testing**
- Add unit tests for each module (RabbitMQ Consumer, InfluxDB Writer, Message Processor) using `pytest`.

### **Publish Test Messages**
You can use RabbitMQ’s management console or CLI to publish test messages:
```bash
rabbitmqadmin publish exchange=amq.default routing_key=your_queue_name payload='{"device.name":"sensor1","timestamp":1672531200,"temperature":25.3}'
```

### **Verify Data in InfluxDB**
Query the `vehicle_data` measurement:
```flux
from(bucket: "your_bucket")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "vehicle_data")
```

---

## **Future Enhancements**
1. **Retry Mechanism**:
   - Add retries for failed RabbitMQ connections and InfluxDB writes.
2. **Metrics and Monitoring**:
   - Integrate with Prometheus or Grafana for monitoring message rates and error counts.
3. **Dead Letter Queue**:
   - Use RabbitMQ’s dead-letter exchange to handle undeliverable messages.
4. **Docker Support**:
   - Containerize the application for easier deployment.

---

## **Contributing**
1. Fork the repository.
2. Create a feature branch:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add new feature"
   ```
4. Push to your fork and submit a pull request.

---

## **License**
This project is licensed under the MIT License.

---

Feel free to copy and paste this **README.md** into your project. Let me know if you’d like any modifications!
