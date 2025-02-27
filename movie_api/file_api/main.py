from contextlib import asynccontextmanager

from api.v1 import file_endpoint
from core.config import settings
from db.minio import close_minio_conn, create_bucket, start_minio_client
from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse
from prometheus_fastapi_instrumentator import Instrumentator


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_minio_client()
    await create_bucket(settings.bucket_name)

    yield
    close_minio_conn()


app = FastAPI(
    title=settings.project_name,
    docs_url="/api/files/openapi",
    openapi_url="/api/files/openapi.json",
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

Instrumentator().instrument(app).expose(app)

app.include_router(file_endpoint.router, prefix="/api/files/v1/file", tags=["files"])

# Эндпойнт для проверки состояния приложения
@app.get("/healthcheck")
async def health_check():
    return {"status": "OK"}
