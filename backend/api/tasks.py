"""
Celery tasks for API integrations.
"""

import os
import json
import logging
from pathlib import Path
from celery import shared_task
import requests

logger = logging.getLogger(__name__)

# Directory for storing API responses
API_RESPONSES_DIR = Path("/app/api_responses")
API_RESPONSES_DIR.mkdir(exist_ok=True)


def _get_api_key(api_alias: str) -> str:
    """Get API key from environment or vault."""
    env_key = f"{api_alias.upper()}_API_KEY"
    api_key = os.getenv(env_key)
    
    if not api_key:
        logger.warning(f"API key for {api_alias} not found in environment")
        return ""
    
    return api_key


@shared_task(bind=True, name='api.tasks.fetch_weather')
def fetch_weather_task(self, city: str, country: str = 'RU'):
    """
    Fetch weather data from OpenWeatherMap API.
    
    Args:
        city: City name
        country: Country code (default: 'RU')
    
    Returns:
        dict: Weather data
    """
    try:
        api_key = _get_api_key('weather')
        if not api_key:
            raise ValueError("Weather API key not found")
        
        url = "https://api.openweathermap.org/data/2.5/weather"
        response = requests.get(url, params={
            'q': f"{city},{country}",
            'appid': api_key,
            'units': 'metric'
        }, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        # Save to file
        filename = API_RESPONSES_DIR / f"weather_{city}_{country}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Weather data saved to {filename}")
        return {
            'status': 'success',
            'city': city,
            'country': country,
            'data': data,
            'file': str(filename)
        }
    except Exception as e:
        logger.error(f"Error fetching weather data: {e}")
        # Update task state
        self.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        raise


@shared_task(bind=True, name='api.tasks.fetch_news')
def fetch_news_task(self, query: str, language: str = 'en'):
    """
    Fetch news data from NewsAPI.
    
    Args:
        query: Search query
        language: Language code (default: 'en')
    
    Returns:
        dict: News data
    """
    try:
        api_key = _get_api_key('news')
        if not api_key:
            raise ValueError("News API key not found")
        
        url = "https://newsapi.org/v2/everything"
        response = requests.get(url, params={
            'q': query,
            'language': language,
            'apiKey': api_key,
            'pageSize': 10
        }, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        # Save to file
        filename = API_RESPONSES_DIR / f"news_{query}_{language}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"News data saved to {filename}")
        return {
            'status': 'success',
            'query': query,
            'language': language,
            'data': data,
            'file': str(filename)
        }
    except Exception as e:
        logger.error(f"Error fetching news data: {e}")
        # Update task state
        self.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        raise

