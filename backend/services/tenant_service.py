"""
Tenant service for multi-tenancy operations.

Handles tenant and organization creation, user assignment, etc.
"""

from sqlalchemy.orm import Session
from database.models import Tenant, Organization, User
from auth.tenant_context import TenantContext
import uuid
import logging

logger = logging.getLogger(__name__)


class TenantService:
    """Service for tenant management."""

    @staticmethod
    def create_tenant(
        db: Session,
        name: str,
        slug: str,
        type: str = "organization",
        subscription_tier: str = "professional"
    ) -> Tenant:
        """Create a new tenant."""
        # Check if slug already exists
        existing = db.query(Tenant).filter(Tenant.slug == slug).first()
        if existing:
            raise ValueError(f"Tenant slug '{slug}' already exists")

        tenant = Tenant(
            id=str(uuid.uuid4()),
            name=name,
            slug=slug,
            type=type,
            subscription_tier=subscription_tier,
            status="active",
            configuration={}
        )
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
        logger.info(f"Created tenant: {tenant.id} ({name})")
        return tenant

    @staticmethod
    def create_organization(
        db: Session,
        tenant_id: str,
        name: str,
        type: str = "organization"
    ) -> Organization:
        """Create an organization within a tenant."""
        # Verify tenant exists
        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            raise ValueError(f"Tenant {tenant_id} not found")

        org = Organization(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            name=name,
            type=type
        )
        db.add(org)
        db.commit()
        db.refresh(org)
        logger.info(f"Created organization: {org.id} in tenant {tenant_id}")
        return org

    @staticmethod
    def assign_user_to_tenant(
        db: Session,
        user_id: str,
        tenant_id: str,
        organization_id: str = None
    ) -> User:
        """Assign a user to a tenant."""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")

        # Verify tenant exists
        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            raise ValueError(f"Tenant {tenant_id} not found")

        # Verify organization exists if provided
        if organization_id:
            org = db.query(Organization).filter(
                Organization.id == organization_id,
                Organization.tenant_id == tenant_id
            ).first()
            if not org:
                raise ValueError(f"Organization {organization_id} not found in tenant")

        user.tenant_id = tenant_id
        user.organization_id = organization_id
        db.commit()
        db.refresh(user)
        logger.info(f"Assigned user {user_id} to tenant {tenant_id}")
        return user

    @staticmethod
    def get_user_tenant(db: Session, user_id: str) -> Tenant:
        """Get the tenant for a user."""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")

        if not user.tenant_id:
            raise ValueError(f"User {user_id} has no tenant assigned")

        tenant = db.query(Tenant).filter(Tenant.id == user.tenant_id).first()
        if not tenant:
            raise ValueError(f"Tenant {user.tenant_id} not found")

        return tenant

    @staticmethod
    def verify_tenant_user_access(
        db: Session,
        user_id: str,
        tenant_id: str
    ) -> bool:
        """Verify that a user has access to a tenant."""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False

        return user.tenant_id == tenant_id or user.is_admin

    @staticmethod
    def enforce_tenant_isolation(
        db: Session,
        user_id: str,
        request_tenant_id: str
    ) -> str:
        """
        Enforce tenant isolation by verifying user access.

        Returns the tenant_id to use for the operation.
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")

        # User's tenant must match request tenant (unless admin)
        if not user.is_admin and user.tenant_id != request_tenant_id:
            raise ValueError(
                f"User {user_id} does not have access to tenant {request_tenant_id}"
            )

        return request_tenant_id
