import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tatarlang.settings')

app = Celery('tatarlang')

# Try to load from celeryconfig.py first, fallback to settings
try:
    app.config_from_object('celeryconfig')
except ImportError:
    # Fallback to Django settings
    app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
