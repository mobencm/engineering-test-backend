from fastapi import APIRouter

from api.endpoints import display ,find , statistics

api_router = APIRouter()
api_router.include_router(display.router, prefix="/display", tags=["display"])
api_router.include_router(find.router, prefix="/find", tags=["find"])
api_router.include_router(statistics.router, prefix="/statistics", tags=["statistics"])
