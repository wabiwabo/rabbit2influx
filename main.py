import logging
from concurrent.futures import ThreadPoolExecutor
from config import Config
from consumers.rabbitmq_consumer import RabbitMQConsumer
from consumers.influxdb_writer import InfluxDBWriter
from consumers.message_processor import MessageProcessor

def main():
    # Load configuration
    config = Config()

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, config.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    logger = logging.getLogger("Main")

    # Initialize components
    influx_writer = InfluxDBWriter(config)
    message_processor = MessageProcessor(influx_writer)

    
    def thread_safe_callback(ch, method, properties, body):
        logger.info(f"Message received: {body.decode('utf-8')}")
        executor.submit(message_processor.process, body)


    # Thread pool
    executor = ThreadPoolExecutor(max_workers=config.max_threads)

    # Start RabbitMQ consumer
    consumer = RabbitMQConsumer(config, thread_safe_callback)
    try:
        consumer.connect()
        consumer.start_consuming()
    except KeyboardInterrupt:
        logger.info("Stopping consumer due to keyboard interrupt.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        executor.shutdown(wait=True)
        consumer.close()

if __name__ == "__main__":
    main()

