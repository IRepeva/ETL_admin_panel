import abc
import json
import os
from typing import Any, Optional

import redis


class BaseStorage:
    @abc.abstractmethod
    def save_state(self, state: dict) -> None:
        """Сохранить состояние в постоянное хранилище"""
        pass

    @abc.abstractmethod
    def retrieve_state(self) -> dict:
        """Загрузить состояние локально из постоянного хранилища"""
        pass


class JsonFileStorage(BaseStorage):
    def __init__(self, file_path: Optional[str] = None):
        self.file_path = file_path

    def is_non_zero_file(self):
        return (os.path.isfile(self.file_path) and
                os.path.getsize(self.file_path) > 0)

    def save_state(self, state: dict):
        current_state = self.retrieve_state()
        current_state.update(state)

        with open(self.file_path, 'w') as storage_file:
            json.dump(current_state, storage_file)

    def retrieve_state(self) -> dict:
        if not self.is_non_zero_file():
            return {}

        with open(self.file_path, 'r') as storage_file:
            return json.load(storage_file)


class RedisStorage(BaseStorage):
    def __init__(self, host='127.0.0.1'):
        self.redis_cache = redis.Redis(host=host, decode_responses=True)

    def save_state(self, state: dict):
        self.redis_cache.mset(state)

    def retrieve_state(self) -> dict:
        all_keys = self.redis_cache.keys()
        if not all_keys:
            return {}
        return dict(zip(all_keys, self.redis_cache.mget(*all_keys)))


class State:
    """
    Класс для хранения состояния при работе с данными, чтобы постоянно не перечитывать данные с начала.
    Здесь представлена реализация с сохранением состояния в файл.
    В целом ничего не мешает поменять это поведение на работу с БД или распределённым хранилищем.
    """

    def __init__(self, storage: BaseStorage):
        self.storage = storage

    def set_state(self, key: str, value: Any) -> None:
        """Установить состояние для определённого ключа"""
        self.storage.save_state({key: value})

    def get_state(self, key: str) -> Any:
        """Получить состояние по определённому ключу"""
        return self.storage.retrieve_state().get(key)
