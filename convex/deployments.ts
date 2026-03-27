import { v } from "convex/values";
import { mutation, query } from "./_generated/server";

export const create = mutation({
  args: {
    deployment_id: v.string(),
    neop: v.string(),
    commit_sha: v.string(),
    branch: v.string(),
    environment: v.union(v.literal("staging"), v.literal("production")),
    status: v.union(v.literal("success"), v.literal("failed"), v.literal("rolled_back")),
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
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("deployments", {
      ...args,
      timestamp: Date.now(),
    });
  },
});

export const get = query({
  args: { deployment_id: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("deployments")
      .filter((q) => q.eq(q.field("deployment_id"), args.deployment_id))
      .first();
  },
});

export const listByNeop = query({
  args: { neop: v.string(), limit: v.optional(v.number()) },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("deployments")
      .withIndex("by_neop", (q) => q.eq("neop", args.neop))
      .order("desc")
      .take(args.limit ?? 20);
  },
});

export const listByEnvironment = query({
  args: {
    environment: v.union(v.literal("staging"), v.literal("production")),
    limit: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("deployments")
      .withIndex("by_environment", (q) => q.eq("environment", args.environment))
      .order("desc")
      .take(args.limit ?? 20);
  },
});

export const listFailed = query({
  args: { limit: v.optional(v.number()) },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("deployments")
      .withIndex("by_status", (q) => q.eq("status", "failed"))
      .order("desc")
      .take(args.limit ?? 20);
  },
});

export const updateStatus = mutation({
  args: {
    deployment_id: v.string(),
    status: v.union(v.literal("success"), v.literal("failed"), v.literal("rolled_back")),
    root_cause: v.optional(v.string()),
    fix_applied: v.optional(v.string()),
    metrics: v.optional(v.object({
      error_rate: v.number(),
      latency_p99_ms: v.number(),
      cpu_percent: v.number(),
      memory_percent: v.number(),
    })),
  },
  handler: async (ctx, args) => {
    const deployment = await ctx.db
      .query("deployments")
      .filter((q) => q.eq(q.field("deployment_id"), args.deployment_id))
      .first();

    if (!deployment) throw new Error(`Deployment ${args.deployment_id} not found`);

    const updates: Record<string, any> = { status: args.status };
    if (args.root_cause) updates.root_cause = args.root_cause;
    if (args.fix_applied) updates.fix_applied = args.fix_applied;
    if (args.metrics) updates.metrics = args.metrics;

    await ctx.db.patch(deployment._id, updates);
  },
});

export const getStats = query({
  args: { neop: v.optional(v.string()), days: v.optional(v.number()) },
  handler: async (ctx, args) => {
    const since = Date.now() - (args.days ?? 30) * 24 * 60 * 60 * 1000;
    let q = ctx.db.query("deployments");
    if (args.neop) {
      q = q.withIndex("by_neop", (idx) => idx.eq("neop", args.neop));
    }

    const all = await q.collect();
    const recent = all.filter((d) => d.timestamp >= since);
    const total = recent.length;
    const successful = recent.filter((d) => d.status === "success").length;
    const failed = recent.filter((d) => d.status === "failed").length;

    return {
      total,
      successful,
      failed,
      rolled_back: recent.filter((d) => d.status === "rolled_back").length,
      success_rate: total > 0 ? (successful / total) * 100 : 0,
      failure_rate: total > 0 ? (failed / total) * 100 : 0,
      avg_duration_ms: total > 0 ? recent.reduce((s, d) => s + d.duration_ms, 0) / total : 0,
      avg_risk_score: total > 0 ? recent.reduce((s, d) => s + d.risk_score, 0) / total : 0,
      avg_cache_hit_rate: total > 0 ? recent.reduce((s, d) => s + d.build_cache_hit_rate, 0) / total : 0,
    };
  },
});
