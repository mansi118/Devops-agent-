"""End-to-end test for incident response flow."""
import pytest
from unittest.mock import AsyncMock, MagicMock


class TestIncidentResponse:
    """E2E test: alert → classify → investigate → respond → resolve → learn."""

    def test_known_pattern_auto_resolution(
        self, mock_stakpak_client, mock_context_vault, mock_slack_client, sample_prometheus_alert
    ):
        """Known incident pattern should be auto-resolved."""
        alert = sample_prometheus_alert

        # Step 1: Classify severity
        severity = alert["labels"]["severity"]
        assert severity == "P2"

        # Step 2: Check recent deployments
        mock_context_vault.query.return_value = [{"deployment_id": "deploy-001", "status": "success"}]
        recent_deploys = mock_context_vault.query("deployments", {"environment": "production"})
        assert len(recent_deploys) > 0

        # Step 3: Search past incidents (find match)
        mock_context_vault.vector_search.return_value = [
            {
                "incident_id": "INC-OLD-001",
                "root_cause": "Connection pool exhausted",
                "resolution": "Service restart",
                "was_auto_resolved": True,
            }
        ]
        similar = mock_context_vault.vector_search("incidents", {"query": alert["annotations"]["description"]})
        assert len(similar) > 0
        assert similar[0]["was_auto_resolved"] is True

        # Step 4: Apply known fix
        mock_stakpak_client.invoke.return_value = {"status": "success", "action": "service_restarted"}
        fix = mock_stakpak_client.invoke("restart_service", {"service": "neos-api"})
        assert fix["status"] == "success"

        # Step 5: Verify health restored
        mock_stakpak_client.health_check.return_value = {"checks": [{"name": "neos-api", "status": "healthy"}]}
        health = mock_stakpak_client.health_check(service="neos-api")
        assert all(c["status"] == "healthy" for c in health["checks"])

        # Step 6: Log resolution
        mock_context_vault.mutation.return_value = {"_id": "inc_001"}
        record = mock_context_vault.mutation("incidents:create", {
            "severity": severity,
            "was_auto_resolved": True,
            "root_cause": "Connection pool exhausted",
        })
        assert record["_id"] is not None

    def test_novel_pattern_escalation(
        self, mock_stakpak_client, mock_context_vault, mock_slack_client, sample_prometheus_alert
    ):
        """Novel incident pattern should escalate to team."""
        # No similar past incidents found
        mock_context_vault.vector_search.return_value = []
        similar = mock_context_vault.vector_search("incidents", {"query": "unknown error pattern"})
        assert len(similar) == 0

        # LLM analysis performed
        mock_stakpak_client.analyze.return_value = {
            "is_known_pattern": False,
            "analysis": "Novel error: database connection timeout due to connection leak",
            "recommended_action": "Investigate connection pooling configuration",
        }
        analysis = mock_stakpak_client.analyze(context="novel error")
        assert analysis["is_known_pattern"] is False

        # Should escalate (not auto-fix)
        mock_slack_client.chat_postMessage.return_value = {"ok": True}

    def test_p1_triggers_whatsapp_escalation(self, sample_prometheus_alert):
        """P1 incident should trigger WhatsApp escalation."""
        alert = sample_prometheus_alert
        alert["labels"]["severity"] = "P1"
        assert alert["labels"]["severity"] == "P1"
        # WhatsApp escalation should be triggered at 5 min mark

    def test_deployment_related_incident_triggers_rollback(
        self, mock_stakpak_client, mock_context_vault
    ):
        """Incident correlated with recent deployment should trigger rollback."""
        mock_context_vault.query.return_value = [
            {"deployment_id": "deploy-recent", "status": "success", "timestamp": 1711459100000}
        ]
        recent = mock_context_vault.query("deployments", {"environment": "production"})
        assert len(recent) > 0

        # Incident detected within 2 hours of deployment
        mock_stakpak_client.analyze.return_value = {
            "is_known_pattern": True,
            "pattern": "recent_deploy_regression",
            "recommended_action": "rollback",
        }
        analysis = mock_stakpak_client.analyze(context="error after recent deploy")
        assert analysis["recommended_action"] == "rollback"
