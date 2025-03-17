# fastapi_mongo_ugc/app/main.py
import sentry_sdk
import uvicorn
from api.v1 import bookmarks, likes, movies, reviews
from core.config import settings
from core.logger import LOGGING
from core.metrics import instrument_bookmarks, instrument_likes, instrument_reviews
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

sentry_sdk.init(
    dsn=settings.sentry_dsn,
    traces_sample_rate=1.0,
    _experiments={
        "continuous_profiling_auto_start": True,
    },
)

app = FastAPI(
    title=settings.project_name,
    docs_url="/api/rating_review_api/openapi",
    openapi_url="/api/rating_review_api/openapi.json",
    default_response_class=ORJSONResponse,
)

instrumentator = Instrumentator()
instrumentator.add(instrument_bookmarks())
instrumentator.add(instrument_likes())
instrumentator.add(instrument_reviews())
instrumentator.instrument(app).expose(app)


@app.get("/sentry-debug")
async def trigger_error():
    division_by_zero = 1 / 0


# Инициализация базы данных
# Base.metadata.create_all(bind=engine)

# Подключение маршрутов
app.include_router(
    movies.router, prefix="/api/rating_review_api/v1/movies", tags=["movies"]
)
app.include_router(
    likes.router, prefix="/api/rating_review_api/v1/likes", tags=["likes"]
)
app.include_router(
    reviews.router, prefix="/api/rating_review_api/v1/reviews", tags=["reviews"]
)
app.include_router(
    bookmarks.router, prefix="/api/rating_review_api/v1/bookmarks", tags=["bookmarks"]
)


# Эндпойнт для проверки состояния приложения
@app.get("/healthcheck")
async def health_check():
    return {"status": "OK"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8766,
        log_config=LOGGING,
        log_level=settings.log_level,
        reload=True,
    )
