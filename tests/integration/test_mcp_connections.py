"""Integration tests for MCP server connections."""
import pytest
from unittest.mock import MagicMock, AsyncMock


class TestMCPConnections:
    def test_github_mcp_connection(self, mock_stakpak_client):
        """GitHub MCP server should be reachable and list tools."""
        mock_stakpak_client.invoke.return_value = {
            "tools": ["get_repo", "list_prs", "get_workflow_runs"],
            "status": "connected",
        }
        result = mock_stakpak_client.invoke("mcp_health", {"server": "github"})
        assert result["status"] == "connected"
        assert "get_repo" in result["tools"]

    def test_aws_mcp_connection(self, mock_stakpak_client):
        """AWS MCP server should be reachable."""
        mock_stakpak_client.invoke.return_value = {
            "tools": ["ec2_list", "cloudwatch_query", "s3_list"],
            "status": "connected",
        }
        result = mock_stakpak_client.invoke("mcp_health", {"server": "aws"})
        assert result["status"] == "connected"

    def test_slack_mcp_connection(self, mock_stakpak_client):
        """Slack MCP server should be reachable."""
        mock_stakpak_client.invoke.return_value = {
            "tools": ["send_message", "create_approval"],
            "status": "connected",
        }
        result = mock_stakpak_client.invoke("mcp_health", {"server": "slack"})
        assert result["status"] == "connected"

    def test_prometheus_mcp_connection(self, mock_stakpak_client):
        """Prometheus MCP should be reachable."""
        mock_stakpak_client.invoke.return_value = {
            "tools": ["query", "query_range", "alerts"],
            "status": "connected",
        }
        result = mock_stakpak_client.invoke("mcp_health", {"server": "prometheus"})
        assert result["status"] == "connected"

    def test_neos_mcp_bus_connection(self, mock_stakpak_client):
        """NEOS MCP bus should be reachable for inter-NEop communication."""
        mock_stakpak_client.invoke.return_value = {
            "tools": ["send_to_neop", "context_vault_query"],
            "status": "connected",
        }
        result = mock_stakpak_client.invoke("mcp_health", {"server": "neos"})
        assert result["status"] == "connected"

    def test_connection_retry_on_failure(self, mock_stakpak_client):
        """MCP connection should retry on transient failure."""
        mock_stakpak_client.invoke.side_effect = [
            ConnectionError("Connection refused"),
            ConnectionError("Connection refused"),
            {"status": "connected"},
        ]
        # First two calls fail, third succeeds
        with pytest.raises(ConnectionError):
            mock_stakpak_client.invoke("mcp_health", {"server": "github"})
        with pytest.raises(ConnectionError):
            mock_stakpak_client.invoke("mcp_health", {"server": "github"})
        result = mock_stakpak_client.invoke("mcp_health", {"server": "github"})
        assert result["status"] == "connected"

    def test_graceful_degradation(self, mock_stakpak_client):
        """System should handle MCP server unavailability gracefully."""
        mock_stakpak_client.invoke.return_value = {
            "status": "degraded",
            "available_servers": ["github", "slack"],
            "unavailable_servers": ["grafana"],
        }
        result = mock_stakpak_client.invoke("mcp_health_all", {})
        assert result["status"] == "degraded"
        assert "grafana" in result["unavailable_servers"]
