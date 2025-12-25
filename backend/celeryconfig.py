"""
Celery configuration file.
"""

import os

# Broker settings
broker_url = os.getenv('CELERY_BROKER_URL', 'amqp://admin:admin@rabbitmq:5672//')

# Result backend
result_backend = 'rpc://'

# Task settings
task_serializer = 'json'
accept_content = ['json']
result_serializer = 'json'
timezone = 'Europe/Moscow'
enable_utc = True

# Task execution settings
task_acks_late = True
task_reject_on_worker_lost = True
worker_prefetch_multiplier = 1

# Task routes (optional)
task_routes = {
    'events.tasks.*': {'queue': 'events'},
    'api.tasks.*': {'queue': 'api'},
}

# Task time limits
task_time_limit = 30 * 60  # 30 minutes
task_soft_time_limit = 25 * 60  # 25 minutes

# Worker settings
worker_max_tasks_per_child = 1000
worker_disable_rate_limits = False

# Beat schedule (can be overridden in settings.py)
beat_schedule = {}

