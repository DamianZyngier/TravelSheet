from fastapi import APIRouter
from .endpoints import countries, admin

api_router = APIRouter()
api_router.include_router(countries.router, prefix="/countries", tags=["countries"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
