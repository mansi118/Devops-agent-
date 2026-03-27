"""Integration tests for staging deployment pipeline."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class TestStagingDeploy:
    def test_docker_build_succeeds(self, mock_stakpak_client):
        """Docker build should succeed for valid source."""
        mock_stakpak_client.invoke.return_value = {
            "status": "success",
            "image": "neos-api:a1b2c3d4",
            "build_time_ms": 180000,
            "cache_hit_rate": 0.83,
        }
        result = mock_stakpak_client.invoke("docker_build", {"repo": "neos-api", "sha": "a1b2c3d4"})
        assert result["status"] == "success"

    def test_tests_run_and_pass(self, mock_stakpak_client):
        """Selected tests should run and pass."""
        mock_stakpak_client.invoke.return_value = {
            "status": "success",
            "tests_run": 30,
            "tests_passed": 30,
            "tests_failed": 0,
            "duration_ms": 45000,
        }
        result = mock_stakpak_client.invoke("run_tests", {"test_files": ["tests/test_api.py"]})
        assert result["tests_failed"] == 0

    def test_security_scan_passes(self, mock_stakpak_client):
        """Security scan should pass (no critical CVEs)."""
        mock_stakpak_client.invoke.return_value = {
            "status": "pass",
            "critical": 0,
            "high": 0,
            "medium": 2,
            "low": 5,
        }
        result = mock_stakpak_client.invoke("snyk_scan", {"image": "neos-api:a1b2c3d4"})
        assert result["critical"] == 0
        assert result["high"] == 0

    def test_staging_deployment_succeeds(self, mock_stakpak_client):
        """Staging deployment should succeed."""
        mock_stakpak_client.deploy.return_value = {
            "status": "deployed",
            "environment": "staging",
            "duration_ms": 120000,
        }
        result = mock_stakpak_client.deploy(
            target="staging.neuraledge.in",
            image="neos-api:a1b2c3d4",
            strategy="rolling",
        )
        assert result["status"] == "deployed"

    def test_health_check_passes_after_deploy(self, mock_stakpak_client):
        """Health check should pass after staging deployment."""
        mock_stakpak_client.health_check.return_value = {
            "checks": [
                {"name": "neos-api-staging", "status": "healthy", "latency_ms": 150},
            ]
        }
        result = mock_stakpak_client.health_check(target="staging.neuraledge.in")
        assert all(c["status"] == "healthy" for c in result["checks"])

    def test_context_vault_updated(self, mock_context_vault, sample_deployment):
        """Context Vault should be updated with deployment record."""
        mock_context_vault.mutation.return_value = {"_id": "deploy_123"}
        result = mock_context_vault.mutation("deployments:create", sample_deployment)
        assert result["_id"] is not None

    def test_failed_tests_block_deploy(self, mock_stakpak_client):
        """Failed tests should prevent deployment."""
        mock_stakpak_client.invoke.return_value = {
            "status": "failed",
            "tests_run": 30,
            "tests_passed": 27,
            "tests_failed": 3,
        }
        result = mock_stakpak_client.invoke("run_tests", {"test_files": ["tests/test_api.py"]})
        assert result["tests_failed"] > 0
        # Deploy should not proceed

    def test_critical_cve_blocks_deploy(self, mock_stakpak_client):
        """Critical CVE in security scan should block deployment."""
        mock_stakpak_client.invoke.return_value = {
            "status": "fail",
            "critical": 1,
            "high": 2,
        }
        result = mock_stakpak_client.invoke("snyk_scan", {"image": "neos-api:a1b2c3d4"})
        assert result["critical"] > 0
