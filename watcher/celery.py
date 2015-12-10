import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'watcher.settings.production')

from django.conf import settings
from celery import Celery

app = Celery('watcher')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
