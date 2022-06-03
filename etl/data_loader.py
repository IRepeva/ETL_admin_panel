import logging
import sys
from typing import List, Dict, Optional

from elasticsearch import helpers, Elasticsearch

sys.path.append('../')
from utils.backoff import backoff


logger = logging.getLogger(__name__)

MOVIES_SETTINGS = {
    'refresh_interval': '1s',
    'analysis': {
        'filter': {
            'english_stop': {
                'type': 'stop',
                'stopwords': '_english_'
            },
            'english_stemmer': {
                'type': 'stemmer',
                'language': 'english'
            },
            'english_possessive_stemmer': {
                'type': 'stemmer',
                'language': 'possessive_english'
            },
            'russian_stop': {
                'type': 'stop',
                'stopwords': '_russian_'
            },
            'russian_stemmer': {
                'type': 'stemmer',
                'language': 'russian'
            }
        },
        'analyzer': {
            'ru_en': {
                'tokenizer': 'standard',
                'filter': [
                    'lowercase',
                    'english_stop',
                    'english_stemmer',
                    'english_possessive_stemmer',
                    'russian_stop',
                    'russian_stemmer'
                ]
            }
        }
    }
}
MOVIES_MAPPING = {
    'dynamic': 'strict',
    'properties': {
        'id': {
            'type': 'keyword'
        },
        'imdb_rating': {
            'type': 'float'
        },
        'genre': {
            'type': 'keyword'
        },
        'title': {
            'type': 'text',
            'analyzer': 'ru_en',
            'fields': {
                'raw': {
                    'type': 'keyword'
                }
            }
        },
        'description': {
            'type': 'text',
            'analyzer': 'ru_en'
        },
        'director': {
            'type': 'text',
            'analyzer': 'ru_en'
        },
        'actors_names': {
            'type': 'text',
            'analyzer': 'ru_en'
        },
        'writers_names': {
            'type': 'text',
            'analyzer': 'ru_en'
        },
        'actors': {
            'type': 'nested',
            'dynamic': 'strict',
            'properties': {
                'id': {
                    'type': 'keyword'
                },
                'name': {
                    'type': 'text',
                    'analyzer': 'ru_en'
                }
            }
        },
        'writers': {
            'type': 'nested',
            'dynamic': 'strict',
            'properties': {
                'id': {
                    'type': 'keyword'
                },
                'name': {
                    'type': 'text',
                    'analyzer': 'ru_en'
                }
            }
        }
    }
}


class ESLoader:
    default_index_name = 'movies'
    default_settings = MOVIES_SETTINGS
    default_mappings = MOVIES_MAPPING

    def __init__(self):
        from config.settings import settings

        self.es = Elasticsearch(settings.ES_DSN)

    @backoff(logger=logger)
    def load(self, data: List[Dict], index_name: str = default_index_name):
        data = self.prepare_for_update(data)
        if not self.es.indices.exists(index=index_name):
            logger.info(
                f'Index "{index_name}" does not exist, '
                f'index creation was started'
            )
            self.create_index(index_name)
        helpers.bulk(
            self.es, data, index=index_name, refresh='wait_for'
        )

    @backoff(logger=logger)
    def create_index(self, index_name: str = default_index_name,
                     settings: Optional[Dict] = None,
                     mappings: Optional[Dict] = None):
        if mappings is None:
            mappings = self.default_mappings
        if settings is None:
            settings = self.default_settings

        self.es.indices.create(index=index_name, ignore=400,
                               body={
                                   'mappings': mappings,
                                   'settings': settings
                               })
        logger.info(f'Index "{index_name}" was created')

    def prepare_for_update(self, data: List[Dict]) -> List[Dict]:
        prepared_data = [
            {
                "_op_type": 'update',
                "_id": str(item['id']),
                "doc": item,
                "doc_as_upsert": True
            } for item in data
        ]
        return prepared_data

    @backoff(logger=logger)
    def search(self, search: Dict, index: str = default_index_name, **kwargs):
        return self.es.search(index=index, body=search, **kwargs)
