from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bean_dailylog.settings')

app = Celery('shortcuts')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()