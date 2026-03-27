"""Shared pytest fixtures for Ops NEop tests."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.fixture
def mock_stakpak_client():
    """Mock Stakpak MCP client."""
    client = MagicMock()
    client.invoke = AsyncMock(return_value={"status": "success"})
    client.deploy = AsyncMock(return_value={"status": "deployed", "duration_ms": 4500})
    client.analyze = AsyncMock(return_value={"risk_score": 3, "analysis": "Low risk change"})
    client.health_check = AsyncMock(return_value={
        "checks": [
            {"name": "NEOS API", "status": "healthy", "latency_ms": 120},
            {"name": "n8n", "status": "healthy", "latency_ms": 85},
            {"name": "OpenClaw", "status": "healthy", "latency_ms": 200},
        ]
    })
    return client


@pytest.fixture
def mock_context_vault():
    """Mock Convex Context Vault client."""
    vault = MagicMock()
    vault.query = AsyncMock(return_value=[])
    vault.mutation = AsyncMock(return_value={"_id": "test_id"})
    vault.vector_search = AsyncMock(return_value=[])
    return vault


@pytest.fixture
def mock_slack_client():
    """Mock Slack client."""
    client = MagicMock()
    client.chat_postMessage = AsyncMock(return_value={"ok": True, "ts": "1234567890.123456"})
    client.chat_update = AsyncMock(return_value={"ok": True})
    client.chat_postEphemeral = AsyncMock(return_value={"ok": True})
    return client


@pytest.fixture
def sample_deployment():
    """Sample deployment data."""
    return {
        "deployment_id": "deploy-001",
        "neop": "neos-api",
        "commit_sha": "a1b2c3d4e5f6",
        "branch": "main",
        "environment": "staging",
        "status": "success",
        "risk_score": 3,
        "actual_outcome": "clean",
        "duration_ms": 245000,
        "test_count": 30,
        "test_total": 400,
        "build_cache_hit_rate": 0.85,
        "metrics": {
            "error_rate": 0.001,
            "latency_p99_ms": 250,
            "cpu_percent": 45,
            "memory_percent": 62,
        },
        "embedding": [0.0] * 1536,
        "timestamp": 1711459200000,
    }


@pytest.fixture
def sample_incident():
    """Sample incident data."""
    return {
        "incident_id": "INC-001",
        "severity": "P2",
        "service": "neos-api",
        "alert_source": "prometheus",
        "root_cause": "Connection pool exhausted",
        "resolution": "Service restarted, pool connections reset",
        "time_to_detect_ms": 30000,
        "time_to_resolve_ms": 180000,
        "runbook_used": "database-connection-pool",
        "was_auto_resolved": True,
        "related_deployment": "deploy-001",
        "embedding": [0.0] * 1536,
        "timestamp": 1711459200000,
    }


@pytest.fixture
def sample_github_push_event():
    """Sample GitHub push webhook payload."""
    return {
        "ref": "refs/heads/main",
        "after": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2",
        "repository": {"name": "neos-api", "full_name": "neuraledge/neos-api"},
        "commits": [
            {
                "id": "a1b2c3d4",
                "message": "feat: add user endpoint",
                "modified": ["src/api/routes.py", "src/api/models.py"],
                "added": ["src/api/user_handler.py"],
                "removed": [],
            }
        ],
    }


@pytest.fixture
def sample_prometheus_alert():
    """Sample Prometheus alert payload."""
    return {
        "status": "firing",
        "labels": {
            "alertname": "HighErrorRate",
            "job": "neos-api",
            "severity": "P2",
            "instance": "13.233.60.59:3000",
        },
        "annotations": {
            "summary": "High error rate on neos-api",
            "description": "Error rate is 8.5% (threshold: 5%).",
        },
        "startsAt": "2026-03-26T14:00:00Z",
    }
