#!/usr/bin/env python3
"""
Test script to demonstrate agent-workflow execution capability.

This script:
1. Creates a test workflow
2. Assigns an agent to it
3. Executes the workflow as the agent
"""

import sys
import asyncio
import logging
from datetime import datetime
from database.db import SessionLocal
from database.models import Workflow, Tenant, User, WorkflowExecution, AgentRun
from services.agent_workflow_executor import AgentWorkflowExecutor
from auth.tenant_context import TenantContext

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_test_tenant():
    """Create a test tenant if it doesn't exist."""
    db = SessionLocal()
    try:
        # Check if test tenant exists
        tenant = db.query(Tenant).filter(
            Tenant.slug == "test-tenant"
        ).first()

        if not tenant:
            logger.info("Creating test tenant...")
            tenant = Tenant(
                name="Test Tenant",
                slug="test-tenant",
                type="school",
                status="active",
            )
            db.add(tenant)
            db.commit()
            logger.info(f"✓ Created test tenant: {tenant.id}")

        return tenant
    finally:
        db.close()


def create_test_user(tenant_id):
    """Create a test user if it doesn't exist."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(
            User.email == "test@example.com",
            User.tenant_id == tenant_id,
        ).first()

        if not user:
            logger.info("Creating test user...")
            user = User(
                email="test@example.com",
                username="testuser",
                tenant_id=tenant_id,
                hashed_password="test_hash",
                role="admin",
            )
            db.add(user)
            db.commit()
            logger.info(f"✓ Created test user: {user.id}")

        return user
    finally:
        db.close()


def create_test_workflow(tenant_id, user_id):
    """Create a test workflow."""
    db = SessionLocal()
    try:
        workflow = Workflow(
            tenant_id=tenant_id,
            creator_id=user_id,
            name="Test Agent Workflow",
            description="Test workflow for agent execution",
            status="active",
            definition={
                "agents": [
                    {
                        "id": "validate_request_and_access",
                        "name": "validate_request_and_access",
                    },
                    {
                        "id": "extract_requirements",
                        "name": "extract_requirements",
                    },
                ]
            },
        )
        db.add(workflow)
        db.commit()
        logger.info(f"✓ Created test workflow: {workflow.id}")
        return workflow
    finally:
        db.close()


def assign_agent_to_workflow(workflow_id, agent_id, tenant_id):
    """Assign an agent to a workflow."""
    db = SessionLocal()
    try:
        workflow = db.query(Workflow).filter(
            Workflow.id == workflow_id,
            Workflow.tenant_id == tenant_id,
        ).first()

        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")

        if workflow.assigned_agents is None:
            workflow.assigned_agents = []

        if agent_id not in workflow.assigned_agents:
            workflow.assigned_agents.append(agent_id)
            db.commit()
            logger.info(f"✓ Assigned agent {agent_id} to workflow {workflow_id}")
        else:
            logger.info(f"Agent {agent_id} already assigned to workflow")

        return workflow
    finally:
        db.close()


async def test_agent_execution():
    """Test agent-workflow execution."""
    logger.info("\n" + "="*80)
    logger.info("AGENT-WORKFLOW EXECUTION TEST")
    logger.info("="*80 + "\n")

    # Create test data
    logger.info("1️⃣  Setting up test environment...")
    tenant = create_test_tenant()
    user = create_test_user(tenant.id)
    workflow = create_test_workflow(tenant.id, user.id)

    # Assign agent to workflow
    logger.info("\n2️⃣  Assigning agent to workflow...")
    agent_id = "extract_requirements"
    assign_agent_to_workflow(workflow.id, agent_id, tenant.id)

    # Execute workflow as agent
    logger.info(f"\n3️⃣  Executing workflow as agent '{agent_id}'...")

    workflow_input = {
        "program_id": "test_program_001",
        "program_name": "Test Program",
        "course_ids": ["course_001"],
        "input_package_id": "pkg_001",
        "input_package_format": "zip",
        "input_skill_framework_id": "framework_001",
    }

    result = await AgentWorkflowExecutor.execute_workflow_for_agent(
        agent_id=agent_id,
        workflow_id=workflow.id,
        tenant_id=tenant.id,
        workflow_input=workflow_input,
    )

    # Display results
    logger.info("\n4️⃣  Execution Results:")
    logger.info("-" * 80)
    logger.info(f"Status: {result['status']}")
    logger.info(f"Execution ID: {result['execution_id']}")
    logger.info(f"Workflow ID: {result['workflow_id']}")
    logger.info(f"Workflow Name: {result.get('workflow_name', 'N/A')}")
    logger.info(f"Agent ID: {result['agent_id']}")

    if result['status'] == 'error':
        logger.error(f"Error: {result.get('error')}")
    else:
        logger.info(f"Result: {result.get('result', {})}")

    # Verify database records
    logger.info("\n5️⃣  Verifying database records...")
    db = SessionLocal()
    try:
        execution = db.query(WorkflowExecution).filter(
            WorkflowExecution.id == result['execution_id']
        ).first()

        if execution:
            logger.info(f"✓ Workflow execution recorded:")
            logger.info(f"  - ID: {execution.id}")
            logger.info(f"  - Status: {execution.status}")
            logger.info(f"  - Started: {execution.started_at}")
            logger.info(f"  - Completed: {execution.completed_at}")

        agent_runs = db.query(AgentRun).filter(
            AgentRun.workflow_execution_id == result['execution_id']
        ).all()

        logger.info(f"✓ Agent runs recorded: {len(agent_runs)}")
        for run in agent_runs:
            logger.info(f"  - Agent: {run.agent_name}")
            logger.info(f"  - Status: {run.status}")
            logger.info(f"  - Started: {run.started_at}")
            logger.info(f"  - Completed: {run.completed_at}")

    finally:
        db.close()

    logger.info("\n" + "="*80)
    logger.info("✓ TEST COMPLETED SUCCESSFULLY")
    logger.info("="*80 + "\n")


def test_get_agent_workflows():
    """Test retrieving workflows assigned to an agent."""
    logger.info("\n" + "="*80)
    logger.info("GET AGENT WORKFLOWS TEST")
    logger.info("="*80 + "\n")

    tenant = create_test_tenant()

    logger.info(f"Getting workflows for agent 'extract_requirements' in tenant {tenant.id}...")
    db = SessionLocal()
    try:
        workflows = AgentWorkflowExecutor.get_agent_workflows(
            agent_id="extract_requirements",
            tenant_id=tenant.id,
            db=db,
        )

        logger.info(f"\n✓ Found {len(workflows)} assigned workflows:")
        for wf in workflows:
            logger.info(f"  - {wf['workflow_name']} (ID: {wf['workflow_id']})")
            logger.info(f"    Automatable: {wf['is_automatable']}")
    finally:
        db.close()


if __name__ == "__main__":
    try:
        # Run async test
        asyncio.run(test_agent_execution())

        # Run sync test
        test_get_agent_workflows()

        logger.info("✓ All tests completed!")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        logger.exception(e)
        sys.exit(1)
