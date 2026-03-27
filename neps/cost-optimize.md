# NeuralEDGE Protocol: Cost Optimization
# Version: 1.0 | Auto-optimized: 2026-03-26T08:00:00Z
# Performance window: Last 30 days

## Metrics (auto-updated)
- total_scans: 0
- savings_identified: 0
- savings_implemented: 0
- idle_resources_found: 0
- right_sizing_recommendations: 0
- reserved_instance_coverage: 0%

## Scanning Schedule

WEEKLY (Monday 9:00 AM IST):
  Full cost analysis and optimization report

DAILY (6:00 AM IST):
  Quick idle resource check

MONTHLY (1st of month):
  Comprehensive billing review and trend analysis

## Decision Rules

### Resource Analysis

IDLE EC2 INSTANCES:
  Definition: CPU < 5% avg over 7 days, no active connections
  → Recommend stop/terminate
  → Calculate monthly savings
  → Check if part of auto-scaling group
  → Verify no scheduled tasks depend on it

ORPHANED EBS VOLUMES:
  Definition: Status = "available" (not attached) for > 7 days
  → Recommend deletion
  → Snapshot first as backup
  → Calculate monthly savings

UNUSED ELASTIC IPS:
  Definition: Not associated with running instance
  → Recommend release
  → Verify no DNS records point to it

OVER-PROVISIONED RDS:
  Definition: CPU < 20% avg, memory < 40%, for 14 days
  → Recommend downgrade instance type
  → Calculate savings
  → Flag if performance SLA at risk

OVER-PROVISIONED EC2:
  Definition: CPU < 30% avg, memory < 50%, for 14 days
  → Recommend right-sizing
  → Suggest specific instance type
  → Calculate savings

OLD/UNUSED DOCKER IMAGES:
  Definition: Not pulled in > 30 days, not tagged as 'latest' or 'production'
  → Recommend cleanup
  → Calculate ECR storage savings

S3 LIFECYCLE GAPS:
  Definition: Buckets without lifecycle policies, data > 90 days
  → Recommend lifecycle policy (IA after 30d, Glacier after 90d)
  → Calculate storage tier savings

### Action Thresholds

AUTO-EXECUTE (no approval):
  - Docker image pruning (untagged, > 7 days old)
  - Log rotation and archival
  - S3 lifecycle policy application (non-production)

RECOMMEND (Slack approval):
  - EC2 stop/terminate
  - EBS volume deletion
  - RDS downgrade
  - Reserved instance purchase

HUMAN-ONLY (report only):
  - Cross-region cost optimization
  - Account-level billing changes
  - Reserved instance commitments > 50,000 INR

## Self-Optimization Rules

1. ACCURACY TRACKING
   - Compare savings estimates with actual billing changes
   - Calibrate estimation models monthly
   - Track which recommendations were accepted vs rejected

2. THRESHOLD ADJUSTMENT
   - If too many false "idle" flags: increase CPU threshold
   - If missed idle resources found manually: decrease threshold
   - Seasonal adjustment for traffic patterns

3. REPORT RELEVANCE
   - Track which report sections get the most engagement
   - Prioritize high-impact findings
   - Remove consistently low-value sections

## Changelog
- [v1.0] Initial protocol created (2026-03-26)
