import logging
import os
import sqlite3
from contextlib import closing

import psycopg2
import redis
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor

from data_loader import SQLiteLoader
from data_saver import PostgresSaver

logger = logging.getLogger('console_logger')

DSL = {
    'dbname': os.environ.get('DB_NAME'),
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'host': os.environ.get('DB_HOST', '127.0.0.1'),
    'port': os.environ.get('DB_PORT', 5432)
}
SQL_PATH = path = os.path.dirname(__file__) + '/db.sqlite'


def transfer_data(sqlite_conn: sqlite3.Connection, pg_conn: _connection):
    sqlite_loader = SQLiteLoader(sqlite_conn)
    postgres_saver = PostgresSaver(pg_conn)

    psycopg2.extras.register_uuid()

    for data, table in sqlite_loader.load_data():
        postgres_saver.save_data(data, table)
    logger.info('All data was successfully loaded')


def check_conn(conn):
    try:
        conn.cursor()
        return True
    except Exception as ex:
        return False


if __name__ == '__main__':
    with closing(sqlite3.connect(SQL_PATH)) as sqlite_conn, \
            closing(
                psycopg2.connect(**DSL, cursor_factory=DictCursor)) as pg_conn:
        transfer_data(sqlite_conn, pg_conn)

    assert not check_conn(sqlite_conn)
    assert not check_conn(pg_conn)
