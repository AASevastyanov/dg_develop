"""
RabbitMQ Producer for sending messages to external API tasks.

This producer connects to RabbitMQ, creates a direct exchange,
and sends messages for API integration tasks.
"""

import os
import json
import pika
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class RabbitMQProducer:
    """Producer for sending messages to RabbitMQ exchange."""
    
    EXCHANGE_NAME = "api_tasks_exchange"
    EXCHANGE_TYPE = "direct"
    
    def __init__(self):
        """Initialize producer with connection parameters from environment."""
        self.connection = None
        self.channel = None
        self._connect()
        self._setup_exchange()
    
    def _get_connection_params(self) -> pika.ConnectionParameters:
        """Get connection parameters from environment variables."""
        # Try to get from vault/secret
        rabbitmq_user = os.getenv('RABBITMQ_USER', 'admin')
        rabbitmq_pass = os.getenv('RABBITMQ_PASS', 'admin')
        rabbitmq_host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
        rabbitmq_port = int(os.getenv('RABBITMQ_PORT', '5672'))
        
        credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)
        return pika.ConnectionParameters(
            host=rabbitmq_host,
            port=rabbitmq_port,
            credentials=credentials,
            heartbeat=600,
            blocked_connection_timeout=300
        )
    
    def _connect(self):
        """Establish connection to RabbitMQ."""
        try:
            params = self._get_connection_params()
            self.connection = pika.BlockingConnection(params)
            self.channel = self.connection.channel()
            logger.info("Connected to RabbitMQ")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise
    
    def _setup_exchange(self):
        """Create durable direct exchange."""
        try:
            self.channel.exchange_declare(
                exchange=self.EXCHANGE_NAME,
                exchange_type=self.EXCHANGE_TYPE,
                durable=True
            )
            logger.info(f"Exchange '{self.EXCHANGE_NAME}' declared (type: {self.EXCHANGE_TYPE})")
        except Exception as e:
            logger.error(f"Failed to declare exchange: {e}")
            raise
    
    def send_api_task(self, api_alias: str, task_params: Dict[str, Any], routing_key: Optional[str] = None):
        """
        Send a message to the exchange for API task execution.
        
        Args:
            api_alias: Alias of the API (e.g., 'weather', 'news')
            task_params: Parameters for the API request
            routing_key: Routing key (defaults to api_alias)
        """
        if routing_key is None:
            routing_key = api_alias
        
        message = {
            'api_alias': api_alias,
            'params': task_params
        }
        
        message_body = json.dumps(message)
        
        try:
            self.channel.basic_publish(
                exchange=self.EXCHANGE_NAME,
                routing_key=routing_key,
                body=message_body,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                )
            )
            logger.info(f"Sent message for API '{api_alias}' with routing key '{routing_key}'")
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            raise
    
    def close(self):
        """Close connection to RabbitMQ."""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("Connection to RabbitMQ closed")


# Convenience function for sending tasks
def send_weather_task(city: str, country: str = None):
    """Send weather API task."""
    producer = RabbitMQProducer()
    try:
        params = {
            'city': city,
            'country': country
        }
        producer.send_api_task('weather', params, routing_key='weather')
    finally:
        producer.close()


def send_news_task(query: str, language: str = 'en'):
    """Send news API task."""
    producer = RabbitMQProducer()
    try:
        params = {
            'query': query,
            'language': language
        }
        producer.send_api_task('news', params, routing_key='news')
    finally:
        producer.close()

