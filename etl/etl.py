from contextlib import closing
from datetime import datetime

import psycopg2
from celery.utils.log import get_task_logger
from psycopg2.extras import DictCursor

from celery_app import app as celery_app
from data_loader import ESLoader
from storage import RedisStorage, State

logger = get_task_logger(__name__)
redis_cache = RedisStorage('redis')
state = State(redis_cache)


@celery_app.task()
def transfer_data():
    from data_extractor import DataExtractor
    from config.settings import settings

    with closing(
            psycopg2.connect(settings.DB_DSN, cursor_factory=DictCursor)
    ) as pg_conn:
        psycopg2.extras.register_uuid()

        state.set_state(DataExtractor.CURRENT_TIME_KEY,
                        datetime.now().isoformat())

        extractor = DataExtractor(pg_conn)
        loader = ESLoader()

        for data, columns in extractor.extract():
            data_for_es = [dict(zip(columns, item)) for item in data]
            loader.load(data_for_es)

    state.set_state(DataExtractor.LAST_EXTRACTED_KEY,
                    state.get_state(DataExtractor.CURRENT_TIME_KEY))

    logger.info(f'All data was successfully transferred to elasticsearch')
