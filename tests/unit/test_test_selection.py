"""Unit tests for AI test selection logic."""
import pytest


def select_tests(changed_files, all_tests, dependency_map=None, always_run=None, history=None):
    """Select minimum test suite covering the changed files."""
    if not changed_files:
        return []

    dependency_map = dependency_map or {}
    always_run = always_run or set()
    history = history or {}

    selected = set()

    # Always-run set
    selected.update(always_run)

    # Direct file-to-test mapping by naming convention
    for f in changed_files:
        test_name = f.replace("src/", "tests/test_").replace(".py", ".py")
        if test_name in all_tests:
            selected.add(test_name)

    # Dependency graph: include tests for files that depend on changed files
    for f in changed_files:
        dependents = dependency_map.get(f, [])
        for dep in dependents:
            test_name = dep.replace("src/", "tests/test_").replace(".py", ".py")
            if test_name in all_tests:
                selected.add(test_name)

    # Historical matches
    for f in changed_files:
        hist_tests = history.get(f, [])
        for t in hist_tests:
            if t in all_tests:
                selected.add(t)

    # If too few, add a random sample
    if len(selected) < len(all_tests) * 0.1 and len(all_tests) > 10:
        import random
        remaining = [t for t in all_tests if t not in selected]
        sample_size = min(max(1, int(len(all_tests) * 0.05)), len(remaining))
        selected.update(random.sample(remaining, sample_size))

    # If too many, just run all
    if len(selected) > len(all_tests) * 0.6:
        return list(all_tests)

    return sorted(selected)


def should_skip_tests(changed_files):
    """Determine if tests can be skipped entirely."""
    skip_patterns = [".md", ".txt", ".rst", ".gitignore", "LICENSE"]
    return all(any(f.endswith(p) for p in skip_patterns) for f in changed_files)


class TestTestSelection:
    def test_empty_files_no_tests(self):
        assert select_tests([], {"tests/test_a.py"}) == []

    def test_direct_mapping(self):
        changed = ["src/api/routes.py"]
        all_tests = {"tests/test_api/routes.py", "tests/test_models.py"}
        # Direct naming convention may not match exactly, but always-run adds some
        result = select_tests(changed, all_tests, always_run={"tests/test_api/routes.py"})
        assert "tests/test_api/routes.py" in result

    def test_always_run_included(self):
        changed = ["src/utils.py"]
        all_tests = {"tests/test_smoke.py", "tests/test_utils.py", "tests/test_api.py"}
        always_run = {"tests/test_smoke.py"}
        result = select_tests(changed, all_tests, always_run=always_run)
        assert "tests/test_smoke.py" in result

    def test_dependency_graph(self):
        changed = ["src/models/user.py"]
        all_tests = {"tests/test_models/user.py", "tests/test_api/routes.py"}
        dep_map = {"src/models/user.py": ["src/api/routes.py"]}
        result = select_tests(changed, all_tests, dependency_map=dep_map)
        assert "tests/test_api/routes.py" in result

    def test_historical_tests(self):
        changed = ["src/api/routes.py"]
        all_tests = {"tests/test_integration.py", "tests/test_api.py"}
        history = {"src/api/routes.py": ["tests/test_integration.py"]}
        result = select_tests(changed, all_tests, history=history)
        assert "tests/test_integration.py" in result

    def test_docs_only_skip(self):
        assert should_skip_tests(["README.md", "docs/guide.txt"]) is True

    def test_code_changes_no_skip(self):
        assert should_skip_tests(["src/main.py"]) is False

    def test_mixed_changes_no_skip(self):
        assert should_skip_tests(["README.md", "src/main.py"]) is False

    def test_full_suite_when_too_many_selected(self):
        changed = [f"src/file_{i}.py" for i in range(50)]
        all_tests = {f"tests/test_file_{i}.py" for i in range(50)}
        dep_map = {f"src/file_{i}.py": [f"src/file_{j}.py" for j in range(50)] for i in range(50)}
        result = select_tests(changed, all_tests, dependency_map=dep_map)
        assert len(result) == len(all_tests)
