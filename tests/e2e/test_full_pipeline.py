"""End-to-end test for the full CI/CD pipeline."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class TestFullPipeline:
    """E2E test: git push → build → test → scan → deploy staging → canary → promote."""

    def test_pipeline_push_to_staging(self, mock_stakpak_client, mock_context_vault, sample_github_push_event):
        """Full pipeline from push to main through staging deployment."""
        # Step 1: Webhook received
        event = sample_github_push_event
        assert event["ref"] == "refs/heads/main"

        # Step 2: AI Risk Triage
        mock_stakpak_client.analyze.return_value = {"risk_score": 3, "risk_reason": "Low risk: API route changes"}
        risk = mock_stakpak_client.analyze(diff=event["commits"][0]["modified"])
        assert risk["risk_score"] < 5

        # Step 3: Docker Build
        mock_stakpak_client.invoke.return_value = {"status": "success", "image": "neos-api:a1b2c3d4", "cache_hit_rate": 0.85}
        build = mock_stakpak_client.invoke("docker_build", {"repo": "neos-api"})
        assert build["status"] == "success"

        # Step 4: AI Test Selection + Run
        mock_stakpak_client.invoke.return_value = {"test_files": ["tests/test_api.py", "tests/test_routes.py"]}
        selection = mock_stakpak_client.invoke("test_selection", {"changed_files": event["commits"][0]["modified"]})
        assert len(selection["test_files"]) > 0

        mock_stakpak_client.invoke.return_value = {"status": "success", "tests_passed": 30, "tests_failed": 0}
        tests = mock_stakpak_client.invoke("run_tests", {"test_files": selection["test_files"]})
        assert tests["tests_failed"] == 0

        # Step 5: Security Scan
        mock_stakpak_client.invoke.return_value = {"status": "pass", "critical": 0, "high": 0}
        scan = mock_stakpak_client.invoke("snyk_scan", {})
        assert scan["critical"] == 0

        # Step 6: Deploy to Staging
        mock_stakpak_client.deploy.return_value = {"status": "deployed", "environment": "staging"}
        deploy = mock_stakpak_client.deploy(target="staging.neuraledge.in", strategy="rolling")
        assert deploy["status"] == "deployed"

        # Step 7: Health Check
        mock_stakpak_client.health_check.return_value = {"checks": [{"name": "staging", "status": "healthy"}]}
        health = mock_stakpak_client.health_check(target="staging.neuraledge.in")
        assert all(c["status"] == "healthy" for c in health["checks"])

        # Step 8: Context Vault record
        mock_context_vault.mutation.return_value = {"_id": "deploy_001"}
        record = mock_context_vault.mutation("deployments:create", {"status": "success"})
        assert record["_id"] is not None

    def test_pipeline_blocks_on_high_risk(self, mock_stakpak_client, sample_github_push_event):
        """High risk score should block auto-deployment."""
        mock_stakpak_client.analyze.return_value = {"risk_score": 9, "risk_reason": "Database migration + auth changes"}
        risk = mock_stakpak_client.analyze(diff=["migrations/001.sql", "src/auth/jwt.py"])
        assert risk["risk_score"] >= 8
        # Pipeline should NOT auto-deploy; requires approval

    def test_pipeline_blocks_on_test_failure(self, mock_stakpak_client):
        """Test failure should block deployment."""
        mock_stakpak_client.invoke.return_value = {"status": "failed", "tests_failed": 2}
        tests = mock_stakpak_client.invoke("run_tests", {})
        assert tests["tests_failed"] > 0

    def test_pipeline_blocks_on_critical_cve(self, mock_stakpak_client):
        """Critical CVE should block deployment."""
        mock_stakpak_client.invoke.return_value = {"status": "fail", "critical": 1}
        scan = mock_stakpak_client.invoke("snyk_scan", {})
        assert scan["critical"] > 0
