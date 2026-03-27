"""Unit tests for NeP (NeuralEDGE Protocol) parsing."""
import pytest
import re
from pathlib import Path


def parse_nep(content: str) -> dict:
    """Parse a NeP markdown file into structured data."""
    result = {
        "name": None,
        "version": None,
        "metrics": {},
        "decision_rules": [],
        "self_optimization_rules": [],
        "changelog": [],
    }

    lines = content.strip().split("\n")

    # Parse header
    for line in lines[:5]:
        if line.startswith("# NeuralEDGE Protocol:"):
            result["name"] = line.replace("# NeuralEDGE Protocol:", "").strip()
        version_match = re.search(r"Version:\s*([\d.]+)", line)
        if version_match:
            result["version"] = version_match.group(1)

    # Parse metrics
    in_metrics = False
    for line in lines:
        if "## Metrics" in line:
            in_metrics = True
            continue
        if line.startswith("## ") and in_metrics:
            in_metrics = False
        if in_metrics and line.startswith("- "):
            parts = line[2:].split(":", 1)
            if len(parts) == 2:
                key = parts[0].strip()
                value = parts[1].strip()
                result["metrics"][key] = value

    # Parse decision rules (section headers under ## Decision Rules)
    in_rules = False
    current_rule = None
    for line in lines:
        if "## Decision Rules" in line:
            in_rules = True
            continue
        if line.startswith("## ") and in_rules and "Decision" not in line:
            in_rules = False
        if in_rules and line.startswith("### "):
            current_rule = line.replace("### ", "").strip()
            result["decision_rules"].append(current_rule)

    # Parse self-optimization rules
    in_optimization = False
    for line in lines:
        if "## Self-Optimization" in line:
            in_optimization = True
            continue
        if line.startswith("## ") and in_optimization and "Self" not in line:
            in_optimization = False
        if in_optimization and re.match(r"^\d+\.\s+\w+", line):
            rule_name = re.sub(r"^\d+\.\s+", "", line).strip()
            result["self_optimization_rules"].append(rule_name)

    # Parse changelog
    in_changelog = False
    for line in lines:
        if "## Changelog" in line:
            in_changelog = True
            continue
        if in_changelog and line.startswith("- "):
            result["changelog"].append(line[2:].strip())

    return result


class TestNepParser:
    @pytest.fixture
    def deploy_nep_content(self):
        return Path("/home/mansigambhir/Documents/devops-agent/neps/deploy.md").read_text()

    def test_parse_name(self, deploy_nep_content):
        result = parse_nep(deploy_nep_content)
        assert result["name"] == "Deployment"

    def test_parse_version(self, deploy_nep_content):
        result = parse_nep(deploy_nep_content)
        assert result["version"] == "1.0"

    def test_parse_metrics(self, deploy_nep_content):
        result = parse_nep(deploy_nep_content)
        assert "total_deployments" in result["metrics"]
        assert "success_rate" in result["metrics"]
        assert "rollback_rate" in result["metrics"]

    def test_parse_decision_rules(self, deploy_nep_content):
        result = parse_nep(deploy_nep_content)
        assert len(result["decision_rules"]) > 0
        assert "Risk-Based Deployment Strategy" in result["decision_rules"]

    def test_parse_self_optimization_rules(self, deploy_nep_content):
        result = parse_nep(deploy_nep_content)
        assert len(result["self_optimization_rules"]) > 0
        assert any("RISK SCORE" in r for r in result["self_optimization_rules"])

    def test_parse_changelog(self, deploy_nep_content):
        result = parse_nep(deploy_nep_content)
        assert len(result["changelog"]) > 0
        assert any("v1.0" in entry for entry in result["changelog"])

    def test_invalid_nep_returns_defaults(self):
        result = parse_nep("This is not a valid NeP file")
        assert result["name"] is None
        assert result["version"] is None
        assert result["metrics"] == {}

    def test_all_neps_parseable(self):
        nep_dir = Path("/home/mansigambhir/Documents/devops-agent/neps")
        for nep_file in nep_dir.glob("*.md"):
            content = nep_file.read_text()
            result = parse_nep(content)
            assert result["name"] is not None, f"{nep_file.name} missing name"
            assert result["version"] is not None, f"{nep_file.name} missing version"
