import logging
import sqlite3
from typing import List

from pydantic import parse_obj_as

from models import table_class_match

logger = logging.getLogger('__name__')


class SQLiteLoader:
    LIMIT = 500

    def __init__(self, sqlite_conn):
        sqlite_conn.row_factory = sqlite3.Row
        self.cursor = sqlite_conn.cursor()

    def load_data(self):
        for table, model in table_class_match.items():
            if not model:
                logger.warning(
                    f'You need to create dataclass for table {table} first'
                )
                continue

            offset = 0
            while 1:
                self.cursor.execute(
                    f'SELECT * '
                    f'FROM {table} '
                    f'LIMIT {self.LIMIT} '
                    f'OFFSET {offset};'
                )
                query_result = self.cursor.fetchall()
                if not query_result:
                    break

                data = [dict(row) for row in query_result]
                items = parse_obj_as(List[model], data)

                yield items, table

                row_fetched = len(query_result)
                if row_fetched < self.LIMIT:
                    break

                offset += row_fetched
