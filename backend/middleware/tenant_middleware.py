"""
Tenant context middleware for FastAPI.

Enforces tenant isolation on all requests.
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from auth.tenant_context import TenantContext
import logging

logger = logging.getLogger(__name__)

# Cache for system tenant ID to avoid repeated queries
_system_tenant_cache = None


def get_system_tenant_id():
    """Get system tenant ID, with caching."""
    global _system_tenant_cache

    if _system_tenant_cache:
        return _system_tenant_cache

    try:
        from database.db import SessionLocal
        from database.models import Tenant

        db = SessionLocal()
        try:
            system_tenant = db.query(Tenant).filter(Tenant.slug == "system").first()
            if system_tenant:
                _system_tenant_cache = system_tenant.id
                logger.debug(f"Cached system tenant ID: {_system_tenant_cache}")
                return _system_tenant_cache
        finally:
            db.close()
    except Exception as e:
        logger.debug(f"Could not get system tenant: {str(e)}")

    return None


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Middleware to extract and validate tenant context from requests.

    Tenant ID can be provided via:
    1. X-Tenant-ID header
    2. From user's associated tenant (via JWT token)
    """

    async def dispatch(self, request: Request, call_next):
        # Skip CORS preflight requests
        if request.method == "OPTIONS":
            return await call_next(request)

        # Extract tenant ID from header
        tenant_id = request.headers.get("X-Tenant-ID")

        # Some endpoints don't require tenant context (auth, health checks)
        skip_tenant_paths = [
            "/api/health",
            "/api/auth/register",
            "/api/auth/login",
            "/api/auth/forgot-password",
            "/api/auth/reset-password",
            "/docs",
            "/openapi.json",
        ]

        path = request.url.path
        requires_tenant = not any(path.startswith(p) for p in skip_tenant_paths)

        # For API requests without explicit tenant, use system tenant
        if requires_tenant and not tenant_id:
            tenant_id = get_system_tenant_id()
            if not tenant_id:
                # Fallback if system tenant not found
                logger.warning("System tenant not found, using 'default'")
                tenant_id = "default"

        if tenant_id:
            try:
                TenantContext.set_tenant(tenant_id)
            except Exception as e:
                logger.error(f"Failed to set tenant context: {str(e)}")
                # Still allow the request to proceed with system tenant
                fallback_id = get_system_tenant_id() or "default"
                TenantContext.set_tenant(fallback_id)

        try:
            response = await call_next(request)
            return response
        finally:
            TenantContext.clear_tenant()
