from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EEE_Final.settings')

app = Celery('EEE_Final')

# Load task modules from all registered Django app configs.
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.update(
    # Other configurations
    broker_url='redis://localhost:6379/0',  # Replace with your Redis configuration
    worker_log_format="[%(levelname)s: %(asctime)s] %(message)s",
    worker_log_color=True,
    worker_log_level="INFO",  # You can adjust the log level here
)
# This line will make sure the app is loaded when Django starts so that task
# decorators can use the app.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


app.conf.worker_log_format = "[%(levelname)s: %(asctime)s] %(message)s"
app.conf.worker_log_color = True
app.conf.worker_log_level = "INFO"  # Set the desired log level here