"""
WSGI config for EEE_Final project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from utils import analyze_test_data, analyze_com_data,get_available_com_ports
import threading


def start_analysis_thread():
    print(f"INFO: Available COM ports: {get_available_com_ports()}")
    print("INFO: Initiating Analyze data thread!")
    analyze_test_data()
    # analyze_com_data()


# Start the analysis thread when the server initializes
analysis_thread = threading.Thread(target=start_analysis_thread)
analysis_thread.start()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EEE_Final.settings')

application = get_wsgi_application()
