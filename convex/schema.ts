import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  deployments: defineTable({
    deployment_id: v.string(),
    neop: v.string(),
    commit_sha: v.string(),
    branch: v.string(),
    environment: v.union(v.literal("staging"), v.literal("production")),
    status: v.union(
      v.literal("success"),
      v.literal("failed"),
      v.literal("rolled_back")
    ),
    risk_score: v.number(),
    actual_outcome: v.string(),
    duration_ms: v.number(),
    test_count: v.number(),
    test_total: v.number(),
    build_cache_hit_rate: v.number(),
    metrics: v.object({
      error_rate: v.number(),
      latency_p99_ms: v.number(),
      cpu_percent: v.number(),
      memory_percent: v.number(),
    }),
    root_cause: v.optional(v.string()),
    fix_applied: v.optional(v.string()),
    embedding: v.array(v.float64()),
    timestamp: v.number(),
  })
    .index("by_neop", ["neop"])
    .index("by_environment", ["environment"])
    .index("by_status", ["status"])
    .vectorIndex("by_embedding", {
      vectorField: "embedding",
      dimensions: 1536,
      filterFields: ["neop", "environment", "status"],
    }),

  incidents: defineTable({
    incident_id: v.string(),
    severity: v.union(
      v.literal("P1"),
      v.literal("P2"),
      v.literal("P3")
    ),
    service: v.string(),
    alert_source: v.string(),
    root_cause: v.string(),
    resolution: v.string(),
    time_to_detect_ms: v.number(),
    time_to_resolve_ms: v.number(),
    runbook_used: v.optional(v.string()),
    was_auto_resolved: v.boolean(),
    related_deployment: v.optional(v.string()),
    embedding: v.array(v.float64()),
    timestamp: v.number(),
  })
    .index("by_severity", ["severity"])
    .index("by_service", ["service"])
    .vectorIndex("by_embedding", {
      vectorField: "embedding",
      dimensions: 1536,
      filterFields: ["severity", "service"],
    }),

  nep_versions: defineTable({
    nep_name: v.string(),
    version: v.number(),
    content: v.string(),
    change_type: v.union(v.literal("auto"), v.literal("manual")),
    change_reason: v.string(),
    metrics_before: v.any(),
    metrics_after: v.optional(v.any()),
    timestamp: v.number(),
  }).index("by_nep", ["nep_name"]),

  audit_log: defineTable({
    action: v.string(),
    agent_id: v.string(),
    profile: v.string(),
    target: v.string(),
    command: v.string(),
    result_code: v.number(),
    approval_source: v.optional(v.string()),
    context: v.any(),
    timestamp: v.number(),
  })
    .index("by_agent", ["agent_id"])
    .index("by_target", ["target"]),
});
