import os

CELERY_BROKER_URL = os.environ.get("BROKER_URL")
CELERY_ACKS_LATE = False
