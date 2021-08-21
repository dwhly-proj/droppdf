import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'droppdf.settings')

from django.conf import settings

app = Celery('droppdf_app', broker=settings.BROKER_URL)

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

BASE_DIR = settings.BASE_DIR

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
