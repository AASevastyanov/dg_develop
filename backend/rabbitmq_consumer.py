"""
RabbitMQ Consumer for processing messages from queues.

This consumer connects to RabbitMQ, creates queues, binds them to exchange,
and processes messages for different API tasks.
"""

import os
import json
import sys
import pika
import logging
from typing import Dict, Any, Callable
import requests
from pathlib import Path

logger = logging.getLogger(__name__)

# Directory for storing API responses
API_RESPONSES_DIR = Path("/app/api_responses")
API_RESPONSES_DIR.mkdir(exist_ok=True)


class RabbitMQConsumer:
    """Consumer for processing messages from RabbitMQ queues."""
    
    EXCHANGE_NAME = "api_tasks_exchange"
    EXCHANGE_TYPE = "direct"
    
    def __init__(self, queue_name: str, routing_key: str):
        """
        Initialize consumer.
        
        Args:
            queue_name: Name of the queue to consume from
            routing_key: Routing key for binding queue to exchange
        """
        self.queue_name = queue_name
        self.routing_key = routing_key
        self.connection = None
        self.channel = None
        self._connect()
        self._setup_queue()
        self._bind_queue()
    
    def _get_connection_params(self) -> pika.ConnectionParameters:
        """Get connection parameters from environment variables."""
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
    
    def _setup_queue(self):
        """Create durable queue."""
        try:
            self.channel.queue_declare(
                queue=self.queue_name,
                durable=True
            )
            logger.info(f"Queue '{self.queue_name}' declared")
        except Exception as e:
            logger.error(f"Failed to declare queue: {e}")
            raise
    
    def _bind_queue(self):
        """Bind queue to exchange with routing key."""
        try:
            # Ensure exchange exists
            self.channel.exchange_declare(
                exchange=self.EXCHANGE_NAME,
                exchange_type=self.EXCHANGE_TYPE,
                durable=True
            )
            
            self.channel.queue_bind(
                exchange=self.EXCHANGE_NAME,
                queue=self.queue_name,
                routing_key=self.routing_key
            )
            logger.info(f"Queue '{self.queue_name}' bound to exchange '{self.EXCHANGE_NAME}' with routing key '{self.routing_key}'")
        except Exception as e:
            logger.error(f"Failed to bind queue: {e}")
            raise
    
    def _get_api_key(self, api_alias: str) -> str:
        """Get API key from vault/environment."""
        # In production, this would fetch from Vault
        # For now, get from environment variable
        env_key = f"{api_alias.upper()}_API_KEY"
        api_key = os.getenv(env_key)
        
        if not api_key:
            # Try to get from vault (would need vault client)
            logger.warning(f"API key for {api_alias} not found in environment")
            return ""
        
        return api_key
    
    def _process_weather_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Process weather API task."""
        api_key = self._get_api_key('weather')
        if not api_key:
            raise ValueError("Weather API key not found")
        
        city = params.get('city', 'Kazan')
        country = params.get('country', 'RU')
        
        # Using OpenWeatherMap API
        url = "https://api.openweathermap.org/data/2.5/weather"
        response = requests.get(url, params={
            'q': f"{city},{country}",
            'appid': api_key,
            'units': 'metric'
        })
        response.raise_for_status()
        
        data = response.json()
        
        # Save to file
        filename = API_RESPONSES_DIR / f"weather_{city}_{country}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Weather data saved to {filename}")
        return data
    
    def _process_news_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Process news API task."""
        api_key = self._get_api_key('news')
        if not api_key:
            raise ValueError("News API key not found")
        
        query = params.get('query', 'technology')
        language = params.get('language', 'en')
        
        # Using NewsAPI
        url = "https://newsapi.org/v2/everything"
        response = requests.get(url, params={
            'q': query,
            'language': language,
            'apiKey': api_key,
            'pageSize': 10
        })
        response.raise_for_status()
        
        data = response.json()
        
        # Save to file
        filename = API_RESPONSES_DIR / f"news_{query}_{language}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"News data saved to {filename}")
        return data
    
    def _process_message(self, ch, method, properties, body):
        """Process incoming message."""
        try:
            message = json.loads(body)
            api_alias = message.get('api_alias')
            params = message.get('params', {})
            
            logger.info(f"Processing message for API: {api_alias}")
            
            # Route to appropriate handler
            if api_alias == 'weather':
                result = self._process_weather_task(params)
            elif api_alias == 'news':
                result = self._process_news_task(params)
            else:
                raise ValueError(f"Unknown API alias: {api_alias}")
            
            # Acknowledge message
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info(f"Message processed successfully for API: {api_alias}")
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            # Reject message and don't requeue
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    
    def start_consuming(self):
        """Start consuming messages from queue."""
        try:
            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=self._process_message
            )
            
            logger.info(f"Waiting for messages in queue '{self.queue_name}'. To exit press CTRL+C")
            self.channel.start_consuming()
        except KeyboardInterrupt:
            logger.info("Stopping consumer...")
            self.channel.stop_consuming()
        except Exception as e:
            logger.error(f"Error in consumer: {e}")
            raise
    
    def close(self):
        """Close connection to RabbitMQ."""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("Connection to RabbitMQ closed")


def main():
    """Main entry point for consumer CLI."""
    if len(sys.argv) < 3:
        print("Usage: python rabbitmq_consumer.py <queue_name> <routing_key>")
        print("Example: python rabbitmq_consumer.py weather_queue weather")
        sys.exit(1)
    
    queue_name = sys.argv[1]
    routing_key = sys.argv[2]
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    consumer = RabbitMQConsumer(queue_name, routing_key)
    try:
        consumer.start_consuming()
    finally:
        consumer.close()


if __name__ == '__main__':
    main()

