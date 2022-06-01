import datetime
import uuid
from typing import ClassVar, Dict, Optional

from pydantic import Field
from pydantic.dataclasses import dataclass


@dataclass
class BaseClass:
    column_mapping: ClassVar[Dict] = {
        'created_at': 'created',
        'updated_at': 'modified'
    }

    @classmethod
    def get_fields(cls):
        return list(cls.__annotations__.keys())


@dataclass
class Filmwork(BaseClass):
    title: str
    type: str
    creation_date: Optional[datetime.date]
    description: Optional[str] = ''
    file_path: Optional[str] = ''
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    rating: Optional[float] = Field(default=0.0, ge=0.0, le=100.0)
    id: uuid.UUID = Field(default_factory=uuid.uuid4)


@dataclass
class Genre(BaseClass):
    name: str
    description: Optional[str] = ''
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    id: uuid.UUID = Field(default_factory=uuid.uuid4)


@dataclass
class GenreFilmwork(BaseClass):
    film_work_id: uuid.UUID
    genre_id: uuid.UUID
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    id: uuid.UUID = Field(default_factory=uuid.uuid4)


@dataclass
class Person(BaseClass):
    full_name: str
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    id: uuid.UUID = Field(default_factory=uuid.uuid4)


@dataclass
class PersonFilmwork(BaseClass):
    film_work_id: uuid.UUID
    person_id: uuid.UUID
    role: str
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    id: uuid.UUID = Field(default_factory=uuid.uuid4)


table_class_match = {
    'film_work': Filmwork,
    'genre': Genre,
    'person': Person,
    'genre_film_work': GenreFilmwork,
    'person_film_work': PersonFilmwork,
}
