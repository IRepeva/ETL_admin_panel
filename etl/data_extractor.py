import logging

from etl import state
from utils.backoff import backoff

logger = logging.getLogger(__name__)


class DataExtractor:
    CURRENT_TIME_KEY = 'current_time'
    LAST_EXTRACTED_KEY = 'last_extracted_time'

    def __init__(self, connection):
        self.current_time = state.get_state(self.CURRENT_TIME_KEY)
        self.last_extracted_time = self.get_last_extracted_time()
        self.connection = connection
        self.cursor = self.connection.cursor()
        self.bunch_size = 5000

    def get_last_extracted_time(self):
        extracted_time = state.get_state(self.LAST_EXTRACTED_KEY)
        return extracted_time if extracted_time else '0001-01-01 00:00:00.000'

    def extract(self):
        fw_ids_persons_changed = self.get_fw_ids_persons_changed()
        fw_ids_genres_changed = self.get_fw_ids_genres_changed()
        film_work_changed = self.get_film_work_changed()

        all_changed_fw_ids = (
                fw_ids_persons_changed |
                fw_ids_genres_changed |
                film_work_changed
        )
        logger.info(f'{len(all_changed_fw_ids)} items were extracted')

        if all_changed_fw_ids:
            str_fw_ids = "', '".join([fw for fw in all_changed_fw_ids])

            pattern, columns = self.get_fw_query_pattern(str_fw_ids)
            self.cursor.execute(pattern)

            data = self.cursor.fetchmany(self.bunch_size)
            while data:
                yield data, columns
                data = self.cursor.fetchmany(self.bunch_size)

    def get_fw_query_pattern(self, str_fw_ids):
        pattern = f'''
            SELECT
                fw.id,
                fw.title,
                fw.description,
                fw.rating,
                COALESCE (
                    ARRAY_AGG(
                        DISTINCT (p.full_name)
                    ) FILTER (WHERE pfw.role = 'director'),
                     '{{}}'
                ) as director,
                COALESCE (
                    ARRAY_AGG(
                        DISTINCT p.full_name
                    ) FILTER (WHERE pfw.role = 'actor'),
                     '{{}}'
                ) as actors_names,
                COALESCE (
                    ARRAY_AGG(
                        DISTINCT p.full_name
                    ) FILTER (WHERE pfw.role = 'writer'),
                     '{{}}'
                ) as writers_names,
                COALESCE (
                   json_agg(
                       DISTINCT jsonb_build_object(
                           'id', p.id,
                           'name', p.full_name
                       )
                   ) FILTER (WHERE p.id IS NOT null AND pfw.role = 'actor'),
                   '[]'
               ) as actors,
                COALESCE (
                   JSON_AGG(
                       DISTINCT jsonb_build_object(
                           'id', p.id,
                           'name', p.full_name
                       )
                   ) FILTER (WHERE p.id IS NOT null AND pfw.role = 'writer'),
                   '[]'
               ) as writers,
               ARRAY_AGG(DISTINCT g.name) as genre
            FROM content.film_work fw
            LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
            LEFT JOIN content.person p ON p.id = pfw.person_id
            LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
            LEFT JOIN content.genre g ON g.id = gfw.genre_id
            WHERE fw.id IN ('{str_fw_ids}')
            GROUP BY fw.id;
        '''
        columns = [
            'id', 'title', 'description', 'imdb_rating', 'director',
            'actors_names', 'writers_names', 'actors', 'writers', 'genre'
        ]
        return pattern, columns

    @backoff(logger=logger)
    def get_fw_ids_persons_changed(self):
        persons_query = f'''
            SELECT id 
            FROM content.person
            WHERE modified 
            BETWEEN '{self.last_extracted_time}' AND '{self.current_time}';
        '''

        self.cursor.execute(persons_query)
        persons = "', '".join([str(per[0]) for per in self.cursor.fetchall()])
        if not persons:
            return set()

        persons_fw_query = f'''
            SELECT fw.id 
            FROM content.film_work fw 
            LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id 
            WHERE pfw.person_id IN ('{persons}');
        '''
        self.cursor.execute(persons_fw_query)

        return {str(fw[0]) for fw in self.cursor.fetchall()}

    @backoff(logger=logger)
    def get_fw_ids_genres_changed(self):
        genres_query = f'''
            SELECT id
            FROM content.genre
            WHERE modified 
            BETWEEN '{self.last_extracted_time}' AND '{self.current_time}';
        '''

        self.cursor.execute(genres_query)
        genres = "', '".join(
            [str(genre[0]) for genre in self.cursor.fetchall()]
        )
        if not genres:
            return set()

        genres_fw_query = f'''
            SELECT fw.id 
            FROM content.film_work fw 
            LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id 
            WHERE gfw.genre_id IN ('{genres}');
        '''
        self.cursor.execute(genres_fw_query)

        return {str(fw[0]) for fw in self.cursor.fetchall()}

    @backoff(logger=logger)
    def get_film_work_changed(self):
        fw_query = f'''
            SELECT id 
            FROM content.film_work
            WHERE modified 
            BETWEEN '{self.last_extracted_time}' AND '{self.current_time}';
        '''
        self.cursor.execute(fw_query)

        return {str(fw[0]) for fw in self.cursor.fetchall()}
