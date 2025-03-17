from typing import List, Optional

from models.genre import Genre
from models.person import Person
from pydantic import BaseModel


class Film(BaseModel):
    """Модель данных кинопроизведения (минимальная - для главной страницы)."""

    uuid: str
    title: str
    imdb_rating: float


class FilmDetailed(Film):
    """Схема данных подробностей о кинопроизведении."""

    genre: Optional[List[Genre]]
    file: Optional[str] = None
    description: Optional[str] = None
    directors_names: Optional[List[str]] = None
    actors_names: Optional[List[str]] = None
    writers_names: Optional[List[str]] = None
    directors: Optional[List[Person]] = None
    actors: Optional[List[Person]] = None
    writers: Optional[List[Person]] = None
