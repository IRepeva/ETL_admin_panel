import sys

from celery.schedules import crontab

sys.path.append('/etl')
import etl


CELERY_BROKER_URL = "redis://redis:6379"
CELERY_RESULT_BACKEND = "redis://redis:6379"

CELERY_BEAT_SCHEDULE = {
    'es_synchronization': {
        'task': 'etl.transfer_data',
        'schedule': crontab(hour=3, minute=0),
        'options': {
            'expires': 15.0,
        },
    },
}
