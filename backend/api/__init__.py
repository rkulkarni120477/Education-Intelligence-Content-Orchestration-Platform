"""
API Routes Module

Centralizes all API endpoints for the application.
"""

from fastapi import APIRouter

# Import route modules
from .courses import router as courses_router

# Create main router
api_router = APIRouter(prefix="/api", tags=["api"])

# Include sub-routers
api_router.include_router(courses_router)

__all__ = ["api_router"]
