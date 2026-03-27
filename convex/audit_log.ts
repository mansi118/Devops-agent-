import { v } from "convex/values";
import { mutation, query } from "./_generated/server";

export const create = mutation({
  args: {
    action: v.string(),
    agent_id: v.string(),
    profile: v.string(),
    target: v.string(),
    command: v.string(),
    result_code: v.number(),
    approval_source: v.optional(v.string()),
    context: v.any(),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("audit_log", {
      ...args,
      timestamp: Date.now(),
    });
  },
});

export const listByAgent = query({
  args: { agent_id: v.string(), limit: v.optional(v.number()) },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("audit_log")
      .withIndex("by_agent", (q) => q.eq("agent_id", args.agent_id))
      .order("desc")
      .take(args.limit ?? 50);
  },
});

export const listByTarget = query({
  args: { target: v.string(), limit: v.optional(v.number()) },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("audit_log")
      .withIndex("by_target", (q) => q.eq("target", args.target))
      .order("desc")
      .take(args.limit ?? 50);
  },
});

export const listRecent = query({
  args: { limit: v.optional(v.number()) },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("audit_log")
      .order("desc")
      .take(args.limit ?? 100);
  },
});
