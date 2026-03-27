# NeuralEDGE Protocol: Deployment
# Version: 1.0 | Auto-optimized: 2026-03-26T08:00:00Z
# Performance window: Last 30 deployments

## Metrics (auto-updated)
- total_deployments: 0
- success_rate: N/A
- avg_deploy_time: N/A
- avg_risk_score: N/A
- rollback_count: 0
- rollback_rate: N/A
- test_reduction_ratio: N/A
- build_cache_hit_rate: N/A
- canary_false_positive_rate: N/A
- canary_false_negative_rate: N/A

## Decision Rules

### Risk-Based Deployment Strategy

IF risk_score >= 8:
  → Block auto-deploy
  → Require senior engineer approval via Slack (#ops-approvals)
  → Run FULL test suite (no AI selection)
  → Deploy to staging only
  → Hold staging for 24 hours before canary consideration
  → Notify ML via WhatsApp

IF risk_score >= 5 AND risk_score < 8:
  → Auto-deploy to staging
  → Run AI-selected tests + all integration tests
  → Canary at 5% traffic for 30 minutes
  → Require ML's Slack approval for full production rollout
  → Post deployment details to #deployments

IF risk_score < 5:
  → Auto-deploy to staging
  → Run AI-selected tests only
  → Canary at 10% traffic for 15 minutes
  → Auto-promote to production if all metrics pass
  → Post summary to #deployments

### Rollback Triggers (any one triggers immediate rollback)
- error_rate > 2% during canary window
- latency_p99 > 2x pre-deploy baseline
- memory_usage > 90% on any pod/instance
- CPU_usage > 85% sustained for 5+ minutes
- any P1 alert fires from the deployed service
- health check failure rate > 10%

### Post-Deploy Actions
1. Generate changelog from commit messages (send to Axe NEop)
2. Update Context Vault deployment log with full metrics
3. Notify #deployments channel with summary
4. If production: notify ML via Chief of Staff daily briefing
5. Record risk_score vs actual_outcome for model calibration

## Self-Optimization Rules

After each deployment, automatically evaluate and adjust:

1. RISK SCORE CALIBRATION
   - Compare predicted risk_score against actual outcome
   - If predicted high risk (>7) but outcome was clean: reduce weight of that risk factor by 5%
   - If predicted low risk (<3) but deployment failed: increase weight by 10%
   - Log calibration change with before/after weights

2. TEST SELECTION ACCURACY
   - After every failed deployment: check if any skipped test would have caught the issue
   - If yes: add that test to "always run" list, increase selection threshold by 2%
   - If no: maintain current threshold
   - Target: 0 false negatives (skipped tests that mattered)

3. CANARY DURATION OPTIMIZATION
   - Track time-to-failure for canary failures
   - If 20 consecutive canaries pass within 10 min: reduce window from 15→10 min
   - If a canary fails after 12+ min: increase window to 20 min
   - Never go below 8 minutes or above 30 minutes

4. BUILD CACHE OPTIMIZATION
   - Track cache hit rate per Dockerfile layer
   - If a layer changes frequently (>50% of builds): move it later in Dockerfile
   - Suggest Dockerfile reordering when hit rate drops below 70%

5. ROLLBACK THRESHOLD TUNING
   - Track false positive rate (rollback triggered but issue was transient)
   - If false_positive_rate > 5%: increase error_rate threshold by 0.5%
   - If false_negative_rate > 0%: decrease threshold by 1%

## Changelog (auto-populated)
- [v1.0] Initial protocol created (2026-03-26)
