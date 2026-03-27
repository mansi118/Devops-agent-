"""Unit tests for AI risk scoring logic."""
import pytest


def calculate_risk_score(changed_files: list, commit_history: list) -> int:
    """Calculate deployment risk score (1-10) based on changed files and history."""
    if not changed_files:
        return 1

    score = 1.0

    high_risk_patterns = [
        "migration", "schema", "auth", "jwt", "oauth",
        "terraform", ".tf", "docker-compose.prod",
        "Dockerfile", "security", "iam", "rbac"
    ]
    medium_risk_patterns = [
        "api", "route", "handler", "controller", "service",
        "model", "database", "config", ".env"
    ]
    low_risk_patterns = [
        ".md", ".txt", ".rst", "test", "spec",
        ".gitignore", "LICENSE", "CHANGELOG"
    ]

    for f in changed_files:
        f_lower = f.lower()
        if any(p in f_lower for p in high_risk_patterns):
            score += 2.0
        elif any(p in f_lower for p in medium_risk_patterns):
            score += 1.0
        elif any(p in f_lower for p in low_risk_patterns):
            score += 0.1

    file_count = len(changed_files)
    if file_count > 20:
        score += 2.0
    elif file_count > 10:
        score += 1.0
    elif file_count > 5:
        score += 0.5

    for record in commit_history:
        if record.get("failures", 0) > 0:
            for f in changed_files:
                if f == record.get("file"):
                    score += min(record["failures"] * 0.5, 2.0)

    return max(1, min(10, round(score)))


def should_run_full_suite(changed_files: list) -> bool:
    """Determine if the full test suite should be run."""
    full_suite_patterns = [
        ".github/workflows", "ci.yml", "cd.yml",
        "Makefile", "docker-compose", "Dockerfile",
        "requirements.txt", "package.json", "Cargo.toml",
        "auth", "jwt", "oauth", "migration", "schema"
    ]
    for f in changed_files:
        f_lower = f.lower()
        if any(p in f_lower for p in full_suite_patterns):
            return True
    return False


class TestRiskScoring:
    def test_low_risk_documentation_only(self):
        changed_files = ["README.md", "docs/api.md", "CHANGELOG.md"]
        score = calculate_risk_score(changed_files, [])
        assert score <= 2

    def test_low_risk_test_only(self):
        changed_files = ["tests/test_api.py", "tests/conftest.py"]
        score = calculate_risk_score(changed_files, [])
        assert score <= 3

    def test_medium_risk_single_service(self):
        changed_files = ["src/api/routes.py", "src/api/models.py"]
        score = calculate_risk_score(changed_files, [])
        assert 3 <= score <= 6

    def test_high_risk_database_changes(self):
        changed_files = ["migrations/001_add_users.sql", "src/models/user.py"]
        score = calculate_risk_score(changed_files, [])
        assert score >= 3

    def test_high_risk_infrastructure_changes(self):
        changed_files = ["terraform/main.tf", "docker-compose.prod.yml"]
        score = calculate_risk_score(changed_files, [])
        assert score >= 5

    def test_high_risk_auth_changes(self):
        changed_files = ["src/auth/middleware.py", "src/auth/jwt.py"]
        score = calculate_risk_score(changed_files, [])
        assert score >= 5

    def test_risk_increases_with_file_count(self):
        few_files = ["src/api/routes.py"]
        many_files = [f"src/api/route_{i}.py" for i in range(20)]
        score_few = calculate_risk_score(few_files, [])
        score_many = calculate_risk_score(many_files, [])
        assert score_many > score_few

    def test_risk_increases_with_failure_history(self):
        changed_files = ["src/api/routes.py"]
        history_clean = []
        history_failures = [{"file": "src/api/routes.py", "failures": 3}]
        score_clean = calculate_risk_score(changed_files, history_clean)
        score_failures = calculate_risk_score(changed_files, history_failures)
        assert score_failures > score_clean

    def test_risk_score_bounds(self):
        test_cases = [
            [],
            ["README.md"],
            [f"src/file_{i}.py" for i in range(100)],
            ["migrations/schema.sql", "src/auth/jwt.py", "terraform/main.tf"],
        ]
        for files in test_cases:
            score = calculate_risk_score(files, [])
            assert 1 <= score <= 10

    def test_ci_config_changes_full_test(self):
        changed_files = [".github/workflows/ci.yml"]
        assert should_run_full_suite(changed_files) is True

    def test_docs_only_no_full_suite(self):
        changed_files = ["README.md", "docs/guide.md"]
        assert should_run_full_suite(changed_files) is False

    def test_empty_files_minimal_risk(self):
        assert calculate_risk_score([], []) == 1
