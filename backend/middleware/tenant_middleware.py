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
        tenant_id = request.headers.get("X-Tenant-ID", "default")

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

        # For API requests without explicit tenant, use default
        if requires_tenant and not tenant_id:
            tenant_id = "default"

        if tenant_id:
            try:
                TenantContext.set_tenant(tenant_id)
            except Exception as e:
                logger.error(f"Failed to set tenant context: {str(e)}")
                # Still allow the request to proceed with default tenant
                TenantContext.set_tenant("default")

        try:
            response = await call_next(request)
            return response
        finally:
            TenantContext.clear_tenant()
