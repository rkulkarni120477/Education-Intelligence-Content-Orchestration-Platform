"""
Multi-tenant context management.

Enforces tenant isolation throughout the application.
Every request must have a valid tenant context.
"""

from typing import Optional
from contextvars import ContextVar
from sqlalchemy.orm import Session

# Context variables for tenant isolation
_tenant_id: ContextVar[Optional[str]] = ContextVar('tenant_id', default=None)


class TenantContext:
    """Manages tenant context for the current request."""

    @staticmethod
    def set_tenant(tenant_id: str) -> None:
        """Set the tenant ID for the current context."""
        if not tenant_id:
            raise ValueError("tenant_id cannot be empty")
        _tenant_id.set(tenant_id)

    @staticmethod
    def get_tenant() -> Optional[str]:
        """Get the current tenant ID."""
        return _tenant_id.get()

    @staticmethod
    def clear_tenant() -> None:
        """Clear the tenant context."""
        _tenant_id.set(None)

    @staticmethod
    def is_set() -> bool:
        """Check if tenant context is set."""
        return _tenant_id.get() is not None


def get_current_tenant_id() -> str:
    """Get the current tenant ID, raising if not set."""
    tenant_id = TenantContext.get_tenant()
    if not tenant_id:
        raise RuntimeError("Tenant context not set. Request must include tenant_id.")
    return tenant_id


def enforce_tenant_isolation(db: Session, model_class, tenant_id: str, **filters):
    """
    Safely query a model with tenant isolation enforcement.

    Args:
        db: SQLAlchemy session
        model_class: The model class to query
        tenant_id: The tenant ID to enforce
        **filters: Additional filter conditions

    Returns:
        Query object
    """
    query = db.query(model_class).filter(model_class.tenant_id == tenant_id)
    for key, value in filters.items():
        column = getattr(model_class, key, None)
        if column is not None:
            query = query.filter(column == value)
    return query
