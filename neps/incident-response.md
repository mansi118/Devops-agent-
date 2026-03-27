# NeuralEDGE Protocol: Incident Response
# Version: 1.0

## Metrics
- total_incidents: 0
- auto_resolved: 0%
- avg_time_to_detect: N/A
- avg_time_to_resolve: N/A
- escalation_rate: N/A

## Severity Classification

P1 (Critical):
  - Service completely down (0 successful health checks)
  - Data loss or corruption detected
  - Security breach confirmed
  → Response: Immediate investigation, WhatsApp escalation at 5 min

P2 (High):
  - Service degraded (error_rate > 5% or latency > 5x normal)
  - Partial functionality loss
  - Security vulnerability actively exploited
  → Response: Investigation + Slack alert, WhatsApp at 15 min

P3 (Medium):
  - Performance degradation (latency > 2x normal)
  - Non-critical component failure
  - Security advisory (not actively exploited)
  → Response: Investigation + Slack alert, no WhatsApp

## Response Playbook

1. DETECT (automated)
   - Source: Prometheus alert, CloudWatch alarm, or health check failure
   - Classify severity using rules above
   - Create incident record in Context Vault

2. INVESTIGATE (automated)
   - Was there a recent deployment? (check last 2 hours)
   - What do application logs show? (fetch last 1000 lines)
   - What do metrics show? (CPU, memory, disk, network, connections)
   - Are other services affected? (check all health endpoints)
   - Is it a known pattern? (Context Vault vector search)
   - Is it a platform issue? (check AWS status, GitHub status)

3. RESPOND (semi-automated)
   Known patterns with auto-fix:
   - "Connection pool exhausted" → restart service, Slack notify
   - "Disk space > 95%" → run cleanup script, Slack notify
   - "OOM killed" → increase memory limit, restart, Slack notify
   - "TLS expired" → auto-renew, restart, Slack notify
   - "Recent deploy caused regression" → auto-rollback, Slack notify

   Unknown patterns:
   - Full analysis sent to Claude API
   - Proposed remediation sent to Slack for human approval
   - If no response in 15 min and P1: escalate via WhatsApp

4. RESOLVE
   - Confirm service health restored
   - Update incident record with root cause and resolution
   - If new pattern: add to known patterns list
   - If caused by deployment: update deploy.md NeP with new rollback trigger

5. LEARN
   - Auto-generate post-mortem template in Notion
   - Update incident embeddings for future similarity search
   - Adjust detection thresholds if too many false positives
   - Update relevant NeP protocols

## Escalation Policy

| Level | Time    | Action                                          |
|-------|---------|------------------------------------------------|
| L0    | 0 min   | Ops auto-investigates, attempts known fixes     |
| L1    | 5 min   | Slack alert to #ops-alerts with analysis        |
| L2    | 15 min  | WhatsApp message to Shivam + Ankit              |
| L3    | 30 min  | WhatsApp message to ML + phone call             |

## Self-Optimization Rules

1. DETECTION ACCURACY
   - Track false positive rate per alert type
   - If > 10% false positives: adjust threshold or add filter
   - If missed incident: add new detection rule

2. RESPONSE TIME
   - Track time from detection to first action
   - If > 60 seconds: optimize investigation pipeline
   - Pre-cache common queries for known patterns

3. PATTERN LIBRARY
   - After each resolved incident, generate signature
   - Test signature against historical incidents
   - Add to auto-fix list if > 90% match accuracy

## Changelog
- [v1.0] Initial protocol created (2026-03-26)
