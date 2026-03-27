# NeuralEDGE Protocol: AI Test Selection
# Version: 1.0 | Auto-optimized: 2026-03-26T08:00:00Z
# Performance window: Last 50 deployments

## Metrics (auto-updated)
- total_selections: 0
- avg_test_reduction: 0%
- false_negative_count: 0
- false_negative_rate: 0%
- avg_selected_tests: 0
- avg_total_tests: 0
- avg_test_time_saved: 0s
- bugs_caught_by_selected: 0
- bugs_missed_by_selection: 0

## Decision Rules

### Test Selection Algorithm

INPUT: git diff (changed files list)

STEP 1 — Dependency Graph Analysis:
  - Parse import/require statements from changed files
  - Build forward dependency graph (what depends on changed files)
  - Build reverse dependency graph (what changed files depend on)
  - Mark all files in dependency cone as "affected"

STEP 2 — Historical Test Mapping:
  - Query Context Vault: which tests have caught bugs in these files before?
  - Weight by recency (recent catches weighted 2x)
  - Weight by frequency (files that break often get more tests)

STEP 3 — Coverage Analysis:
  - Map affected files to test files via naming convention
  - Map affected files to test files via coverage data (if available)
  - Include tests that import affected modules

STEP 4 — Always-Run Set:
  - Smoke tests (critical path verification)
  - Integration tests for changed services
  - Security tests
  - Tests on the "always run" list (from false negative learning)

STEP 5 — Selection:
  - Union of: STEP 1 tests + STEP 2 tests + STEP 3 tests + STEP 4 tests
  - Deduplicate
  - Sort by priority (historical bug catch rate)
  - If total < 10% of full suite: add random 5% sample for coverage
  - If total > 60% of full suite: just run full suite

### Override Rules

RUN FULL SUITE when:
  - Risk score >= 8
  - Changes touch CI/CD configuration
  - Changes touch shared libraries/utilities
  - Changes touch authentication/authorization code
  - Changes touch database schema
  - First deployment of a new service
  - Manual override via Slack command

SKIP TESTS when:
  - Only documentation files changed (.md, .txt, .rst)
  - Only comments changed (verified by AST diff)
  - Only whitespace/formatting changed
  - Dependency lock file only update (still run security scan)

## Self-Optimization Rules

1. FALSE NEGATIVE TRACKING
   After every failed deployment:
   - Check if any SKIPPED test would have caught the issue
   - If yes:
     a. Add that test to "always run" list
     b. Increase selection threshold by 2%
     c. Log the miss with file-to-test mapping
     d. Alert team: "Test selection missed: [test] for [file]"
   - TARGET: 0 false negatives

2. OVER-SELECTION REDUCTION
   After every successful deployment:
   - Check which selected tests actually tested changed code paths
   - If a test was selected but didn't exercise any changed code:
     a. Reduce its selection weight by 5%
     b. Don't remove it entirely (safety margin)

3. SPEED OPTIMIZATION
   - Track per-test execution time
   - Parallelize independent test groups
   - Suggest test splitting for slow tests (> 30s)

4. HISTORICAL ACCURACY
   - Monthly: compare predicted test relevance vs actual code paths
   - Recalibrate dependency graph weights
   - Update file-to-test mappings from coverage data

## Changelog
- [v1.0] Initial protocol created (2026-03-26)
