import { v } from "convex/values";
import { mutation, query } from "./_generated/server";

export const create = mutation({
  args: {
    incident_id: v.string(),
    severity: v.union(v.literal("P1"), v.literal("P2"), v.literal("P3")),
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
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("incidents", {
      ...args,
      timestamp: Date.now(),
    });
  },
});

export const get = query({
  args: { incident_id: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("incidents")
      .filter((q) => q.eq(q.field("incident_id"), args.incident_id))
      .first();
  },
});

export const listBySeverity = query({
  args: {
    severity: v.union(v.literal("P1"), v.literal("P2"), v.literal("P3")),
    limit: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("incidents")
      .withIndex("by_severity", (q) => q.eq("severity", args.severity))
      .order("desc")
      .take(args.limit ?? 20);
  },
});

export const listByService = query({
  args: { service: v.string(), limit: v.optional(v.number()) },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("incidents")
      .withIndex("by_service", (q) => q.eq("service", args.service))
      .order("desc")
      .take(args.limit ?? 20);
  },
});

export const updateResolution = mutation({
  args: {
    incident_id: v.string(),
    root_cause: v.string(),
    resolution: v.string(),
    time_to_resolve_ms: v.number(),
    was_auto_resolved: v.boolean(),
  },
  handler: async (ctx, args) => {
    const incident = await ctx.db
      .query("incidents")
      .filter((q) => q.eq(q.field("incident_id"), args.incident_id))
      .first();
    if (!incident) throw new Error(`Incident ${args.incident_id} not found`);
    await ctx.db.patch(incident._id, {
      root_cause: args.root_cause,
      resolution: args.resolution,
      time_to_resolve_ms: args.time_to_resolve_ms,
      was_auto_resolved: args.was_auto_resolved,
    });
  },
});

export const getStats = query({
  args: { days: v.optional(v.number()) },
  handler: async (ctx, args) => {
    const since = Date.now() - (args.days ?? 30) * 24 * 60 * 60 * 1000;
    const all = await ctx.db.query("incidents").collect();
    const recent = all.filter((i) => i.timestamp >= since);
    const total = recent.length;
    const autoResolved = recent.filter((i) => i.was_auto_resolved).length;

    return {
      total,
      auto_resolved: autoResolved,
      auto_resolve_rate: total > 0 ? (autoResolved / total) * 100 : 0,
      p1_count: recent.filter((i) => i.severity === "P1").length,
      p2_count: recent.filter((i) => i.severity === "P2").length,
      p3_count: recent.filter((i) => i.severity === "P3").length,
      avg_time_to_detect_ms: total > 0 ? recent.reduce((s, i) => s + i.time_to_detect_ms, 0) / total : 0,
      avg_time_to_resolve_ms: total > 0 ? recent.reduce((s, i) => s + i.time_to_resolve_ms, 0) / total : 0,
    };
  },
});
