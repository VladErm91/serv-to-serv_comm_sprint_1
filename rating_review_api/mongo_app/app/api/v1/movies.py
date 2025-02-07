from logging import getLogger

from core.config import db
from core.jwt import security_jwt
from core.utils import convert_objectid
from fastapi import APIRouter, Depends
from schemas.schemas import Movie, MovieCreate
from typing_extensions import Annotated

logger = getLogger().getChild("movies-router")

router = APIRouter()


@router.post("/", response_model=Movie)
async def create_movie(
    movie: MovieCreate, user: Annotated[dict, Depends(security_jwt)]
):
    """
    Create a new movie.

    Args:
        movie: MovieCreate - The movie object containing the title and description.

    Returns:
        The created Movie object from the database.
    """
    movie_dict = movie.model_dump()
    logger.info(f"movie_dict: {movie_dict}")
    result = await db.movies.insert_one(movie_dict)
    created_movie = convert_objectid(
        await db.movies.find_one({"_id": result.inserted_id})
    )
    return created_movie
