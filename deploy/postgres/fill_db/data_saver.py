import logging
from dataclasses import asdict

import psycopg2.extras

from models import table_class_match

logger = logging.getLogger(__name__)


def get_corresponding_columns(table):
    dc_model = table_class_match[table]

    source_columns = dc_model.get_fields()
    target_columns = [
        dc_model.column_mapping.get(col, col) for col in source_columns
    ]
    return source_columns, target_columns


class PostgresSaver:
    _cached_table = None
    _pattern = None
    _on_conflict = 'NOTHING'
    _on_conflict_cols = 'id'

    def __init__(self, pg_conn):
        self.connection = pg_conn
        self.cursor = pg_conn.cursor()

    def get_insert_pattern(self, table):
        source_columns, target_columns = get_corresponding_columns(table)

        s_values = ', '.join([f'%({column})s' for column in source_columns])
        pattern = f'''
            INSERT INTO content.{table} ({', '.join(target_columns)}) 
            VALUES ({s_values}) 
            ON CONFLICT ("{self._on_conflict_cols}") 
            DO {self._on_conflict};
        '''
        return pattern

    def save_data(self, data, table):
        data = [asdict(item) for item in data]

        if self._cached_table != table:
            self._cached_table = table
            self._pattern = self.get_insert_pattern(table)

        try:
            psycopg2.extras.execute_batch(
                self.cursor, self._pattern, data, page_size=1000
            )
            self.connection.commit()
        except psycopg2.Error as e:
            logger.error(e.pgerror)
            self.connection.rollback()
