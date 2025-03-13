# app/api/v1/api.py
from api.v1.endpoints import notifications
from fastapi import APIRouter

api_router = APIRouter()

api_router.include_router(
    notifications.router, prefix="/notifications", tags=["notifications"]
)
