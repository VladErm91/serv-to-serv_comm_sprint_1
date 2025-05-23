from contextlib import asynccontextmanager

from api.v1 import films, genres, persons
from core.config import settings
from core.metrics import instrument_film, instrument_person
from core.tracer import configure_tracer
from db import elastic
from db.redis import get_cache_service
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from prometheus_fastapi_instrumentator import Instrumentator


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = get_cache_service()
    elastic.es = AsyncElasticsearch(
        hosts=[
            f"{settings.elastic_schema}{settings.elastic_host}:{settings.elastic_port}"
        ]
    )

    yield
    # Закрытие клиентов
    await redis.close()
    await elastic.es.close()


app = FastAPI(
    title=settings.project_name,
    docs_url="/api/movies/openapi",
    openapi_url="/api/movies/openapi.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)


@app.middleware("http")
async def before_request(request: Request, call_next):
    # Разрешаем запросы к /metrics без X-Request-Id
    if request.url.path.startswith("/metrics"):
        return await call_next(request)

    request_id = request.headers.get("X-Request-Id")
    if not request_id:
        return ORJSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "X-Request-Id is required"},
        )

    response = await call_next(request)
    return response


if settings.enable_tracing:
    configure_tracer()
    # FastAPIInstrumentor.instrument_app(app)

instrumentator = Instrumentator()
instrumentator.add(instrument_person())
instrumentator.add(instrument_film())
instrumentator.instrument(app).expose(app)

app.include_router(films.router, prefix="/api/v1/films", tags=["films"])
app.include_router(persons.router, prefix="/api/v1/persons", tags=["persons"])
app.include_router(genres.router, prefix="/api/v1/genres", tags=["genres"])


# Эндпойнт для проверки состояния приложения
@app.get("/healthcheck")
async def health_check():
    return {"status": "OK"}
