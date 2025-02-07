import logging
from typing import Dict

from database import get_genres, get_names, get_persons
from models import Movie

logger = logging.getLogger(__name__)


def transform_movie(movie_row: Dict) -> Dict:
    """Transform a database row to a dictionary for Elasticsearch."""
    movie_id = str(movie_row["id"])
    description = movie_row.get("description", "") or ""
    imdb_rating = movie_row.get("rating")
    file = movie_row.get("file", "") or ""
    creation_date = movie_row.get("creation_date") or ""

    if not description:
        description = ""
    if not file:
        file = ""
    if not creation_date:
        creation_date = ""

    try:
        genres = get_genres(movie_id)
        directors_names = get_names(movie_id, "director")
        actors_names = get_names(movie_id, "actor")
        writers_names = get_names(movie_id, "writer")
        directors = get_persons(movie_id, "director")
        actors = get_persons(movie_id, "actor")
        writers = get_persons(movie_id, "writer")
    except Exception as e:
        logger.error(f"Error retrieving genres for movie ID: {movie_id}: {e}")
        genres = directors_names = actors_names = writers_names = []
        directors = actors = writers = []

    movie = Movie(
        uuid=movie_id,
        imdb_rating=imdb_rating if imdb_rating is not None else None,
        genre=genres,
        title=movie_row["title"],
        description=description,
        file=file,
        creation_date=creation_date if creation_date else None,
        directors_names=directors_names,
        actors_names=actors_names,
        writers_names=writers_names,
        directors=directors,
        actors=actors,
        writers=writers,
    )
    return movie.model_dump()


def transform_genre(genre_row):
    return {
        "uuid": str(genre_row["id"]),
        "name": genre_row["name"],
    }


def transform_person(person_row):
    return {
        "uuid": str(person_row["id"]),
        "full_name": person_row["full_name"],
        "modified": person_row["modified"],
    }
