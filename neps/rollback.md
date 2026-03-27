# NeuralEDGE Protocol: Rollback
# Version: 1.0 | Auto-optimized: 2026-03-26T08:00:00Z
# Performance window: Last 30 rollbacks

## Metrics (auto-updated)
- total_rollbacks: 0
- auto_rollbacks: 0
- manual_rollbacks: 0
- avg_rollback_time: N/A
- false_positive_rate: 0%
- data_loss_incidents: 0
- successful_recovery_rate: N/A

## Decision Rules

### When to Rollback

IMMEDIATE AUTO-ROLLBACK (no human approval needed):
  Triggered during canary observation window:
  - error_rate > 2% (baseline + threshold)
  - latency_p99 > 2x pre-deploy baseline
  - memory_usage > 90% on any instance
  - CPU_usage > 85% sustained for 5+ minutes
  - health_check_failure_rate > 10%
  - any P1 alert fires from deployed service

RECOMMENDED ROLLBACK (requires human approval):
  Triggered post-promotion:
  - error_rate increase > 1% compared to pre-deploy (sustained 10 min)
  - user-reported issues correlated with deployment
  - performance degradation detected by monitoring
  - security vulnerability discovered in deployed code

### Rollback Strategy

FOR CANARY DEPLOYMENTS:
  1. Shift 100% traffic back to previous version
  2. Remove canary instances
  3. Verify health of previous version
  4. Log rollback reason and metrics in Context Vault
  5. Create GitHub Issue with failure analysis
  6. Notify #deployments and #ops-alerts

FOR FULL DEPLOYMENTS:
  1. Identify last known good version from Context Vault
  2. Verify last known good image exists in ECR
  3. Deploy previous version using rolling strategy
  4. Monitor for 10 minutes post-rollback
  5. If stable: mark deployment as rolled_back in Context Vault
  6. If unstable: escalate to P1, notify on-call

FOR DATABASE-COUPLED DEPLOYMENTS:
  → NEVER auto-rollback
  → Flag as "requires human review"
  → Notify senior engineer with migration analysis
  → Document forward-fix vs rollback options

### Pre-Rollback Checks
1. Verify previous image exists and is pullable
2. Check if database migrations were applied (block auto-rollback if yes)
3. Ensure no other deployment is in progress
4. Snapshot current state for post-mortem

### Post-Rollback Actions
1. Verify service health (5 health checks over 2 minutes)
2. Compare metrics to pre-deploy baseline
3. Update Context Vault with rollback record
4. Generate incident report
5. Notify team via Slack with:
   - What was deployed
   - Why it was rolled back
   - Current system status
   - Next steps / assignee for fix
6. Update deploy.md NeP with new failure pattern

## Self-Optimization Rules

1. THRESHOLD TUNING
   - Track false positive rate (rollback triggered but issue was transient)
   - If false_positive_rate > 5%: increase error_rate threshold by 0.5%
   - If a bad deploy slips through: decrease threshold by 1%
   - Log all threshold changes

2. ROLLBACK SPEED
   - Track time from trigger to recovery
   - If rollback takes > 5 min: investigate bottleneck
   - Optimize by pre-pulling previous images during canary

3. PATTERN RECOGNITION
   - After each rollback, categorize the failure type
   - Build library of failure signatures for faster detection
   - Feed patterns into deploy.md risk scoring

## Changelog
- [v1.0] Initial protocol created (2026-03-26)
