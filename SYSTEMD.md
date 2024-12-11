# Rabbit2Influx Service Documentation

## Overview
This documentation provides instructions for setting up the `Rabbit2Influx` Python application as a systemd service on a Linux system. The application is located in the `/opt/rabbit2influx` directory and uses a Python virtual environment.

## Directory Structure
The application structure is as follows:

```
/opt/rabbit2influx
|-- main.py                # Main application script
|-- venv-r2i/              # Virtual environment
|-- requirements.txt       # Application dependencies
|-- .env                   # Environment variables
|-- .env.dev               # Development environment variables
|-- config.py              # Configuration file
|-- consumers/             # Directory for consumers
    |-- influxdb_writer.py    # Handles writing to InfluxDB
    |-- message_processor.py  # Processes messages
    |-- rabbitmq_consumer.py  # Consumes messages from RabbitMQ
```

## Setting Up the Service

### Step 1: Install Dependencies
Ensure all required dependencies are installed in the virtual environment:

```bash
cd /opt/rabbit2influx
python3 -m venv venv-r2i
source venv-r2i/bin/activate
pip install -r requirements.txt
```

### Step 2: Create a systemd Service File
Create a service file to manage the application using `systemd`.

1. Open a terminal and create a new service file:
   ```bash
   sudo nano /etc/systemd/system/rabbit2influx.service
   ```

2. Add the following configuration to the file:

   ```ini
   [Unit]
   Description=Rabbit to InfluxDB Python Application
   After=network.target

   [Service]
   User=your_username
   Group=your_groupname
   WorkingDirectory=/opt/rabbit2influx
   ExecStart=/opt/rabbit2influx/venv-r2i/bin/python3 /opt/rabbit2influx/main.py
   Restart=always
   RestartSec=5
   Environment=PYTHONUNBUFFERED=1
   EnvironmentFile=/opt/rabbit2influx/.env

   [Install]
   WantedBy=multi-user.target
   ```

   **Notes:**
   - Replace `your_username` with the username running the service.
   - Replace `your_groupname` with the user's group.

### Step 3: Reload systemd and Start the Service
Reload systemd to apply the changes and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable rabbit2influx.service
sudo systemctl start rabbit2influx.service
```

### Step 4: Verify the Service
Check the service status to ensure it is running:

```bash
sudo systemctl status rabbit2influx.service
```

## Optional: Use a Wrapper Script
If the application requires activating the virtual environment explicitly, you can create a wrapper script:

1. Create the wrapper script:
   ```bash
   nano /opt/rabbit2influx/run.sh
   ```

2. Add the following lines to the script:
   ```bash
   #!/bin/bash
   source /opt/rabbit2influx/venv-r2i/bin/activate
   python3 /opt/rabbit2influx/main.py
   ```

3. Make the script executable:
   ```bash
   chmod +x /opt/rabbit2influx/run.sh
   ```

4. Update the service file's `ExecStart` directive:
   ```ini
   ExecStart=/bin/bash /opt/rabbit2influx/run.sh
   ```

Reload and restart the service:
```bash
sudo systemctl daemon-reload
sudo systemctl restart rabbit2influx.service
```

## Logs
To capture application logs, update the service file to include logging:

```ini
[Service]
StandardOutput=append:/var/log/rabbit2influx.log
StandardError=append:/var/log/rabbit2influx_error.log
```

Create the log files and set permissions:
```bash
sudo mkdir -p /var/log
sudo touch /var/log/rabbit2influx.log /var/log/rabbit2influx_error.log
sudo chmod 664 /var/log/rabbit2influx*.log
```

## Managing the Service
Use the following commands to manage the service:

- **Start the service:**
  ```bash
  sudo systemctl start rabbit2influx.service
  ```

- **Stop the service:**
  ```bash
  sudo systemctl stop rabbit2influx.service
  ```

- **Restart the service:**
  ```bash
  sudo systemctl restart rabbit2influx.service
  ```

- **Check service status:**
  ```bash
  sudo systemctl status rabbit2influx.service
  ```

- **Enable service on boot:**
  ```bash
  sudo systemctl enable rabbit2influx.service
  ```

- **Disable service on boot:**
  ```bash
  sudo systemctl disable rabbit2influx.service
  ```

## Conclusion
This documentation provides a step-by-step guide to configure and manage the `Rabbit2Influx` Python application as a systemd service. For any issues, review the logs or verify the service configuration.


