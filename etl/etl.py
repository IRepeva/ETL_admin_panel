import os
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

DSL = {
    'dbname': os.environ.get('DB_NAME'),
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'host': os.environ.get('DB_HOST', '127.0.0.1'),
    'port': os.environ.get('DB_PORT', 5432)
}


@celery_app.task()
def transfer_data():
    from data_extractor import DataExtractor

    with closing(psycopg2.connect(**DSL, cursor_factory=DictCursor)) as pg_conn:
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


if __name__ == '__main__':
    with closing(psycopg2.connect(**DSL, cursor_factory=DictCursor)) as pg_conn:
        psycopg2.extras.register_uuid()
        transfer_data(pg_conn)
