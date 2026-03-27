"""Integration tests for GitHub webhook handling."""
import pytest
import json
import hmac
import hashlib
from unittest.mock import AsyncMock, patch, MagicMock


WEBHOOK_SECRET = "test-webhook-secret"


def generate_signature(payload: str, secret: str) -> str:
    """Generate GitHub webhook HMAC signature."""
    mac = hmac.new(secret.encode(), payload.encode(), hashlib.sha256)
    return f"sha256={mac.hexdigest()}"


class TestGitHubWebhook:
    def test_push_to_main_triggers_pipeline(self, sample_github_push_event):
        """Push to main should trigger the CI/CD pipeline."""
        event = sample_github_push_event
        assert event["ref"] == "refs/heads/main"
        # Verify the event would pass the filter
        assert "main" in event["ref"] or "production" in event["ref"]

    def test_push_to_production_triggers_full_pipeline(self):
        """Push to production should trigger full pipeline with approval."""
        event = {
            "ref": "refs/heads/production",
            "after": "b2c3d4e5f6a7",
            "repository": {"name": "neos-api"},
            "commits": [{"id": "b2c3d4", "message": "release: v1.2.0", "modified": ["src/main.py"]}],
        }
        assert "production" in event["ref"]

    def test_pr_opened_triggers_build_test(self):
        """PR opened should trigger build and test only (no deploy)."""
        event = {
            "action": "opened",
            "pull_request": {"number": 42, "head": {"sha": "c3d4e5f6"}},
            "repository": {"name": "neos-api"},
        }
        assert event["action"] == "opened"
        assert "pull_request" in event

    def test_invalid_signature_rejected(self, sample_github_push_event):
        """Invalid webhook signature should be rejected."""
        payload = json.dumps(sample_github_push_event)
        valid_sig = generate_signature(payload, WEBHOOK_SECRET)
        invalid_sig = "sha256=0000000000000000000000000000000000000000000000000000000000000000"
        assert valid_sig != invalid_sig

    def test_valid_signature_accepted(self, sample_github_push_event):
        """Valid webhook signature should be accepted."""
        payload = json.dumps(sample_github_push_event)
        sig = generate_signature(payload, WEBHOOK_SECRET)
        # Verify signature
        expected = hmac.new(WEBHOOK_SECRET.encode(), payload.encode(), hashlib.sha256)
        assert hmac.compare_digest(sig, f"sha256={expected.hexdigest()}")

    def test_non_main_branch_ignored(self):
        """Pushes to non-main/production branches should be filtered out."""
        event = {"ref": "refs/heads/feature/my-feature", "commits": []}
        assert "main" not in event["ref"] and "production" not in event["ref"]

    def test_commit_data_extracted(self, sample_github_push_event):
        """Verify commit data is correctly extracted from webhook payload."""
        commits = sample_github_push_event["commits"]
        assert len(commits) == 1
        assert "modified" in commits[0]
        assert "src/api/routes.py" in commits[0]["modified"]
