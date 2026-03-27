import { v } from "convex/values";
import { mutation, query } from "./_generated/server";

export const create = mutation({
  args: {
    nep_name: v.string(),
    version: v.number(),
    content: v.string(),
    change_type: v.union(v.literal("auto"), v.literal("manual")),
    change_reason: v.string(),
    metrics_before: v.any(),
    metrics_after: v.optional(v.any()),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("nep_versions", {
      ...args,
      timestamp: Date.now(),
    });
  },
});

export const getLatest = query({
  args: { nep_name: v.string() },
  handler: async (ctx, args) => {
    const versions = await ctx.db
      .query("nep_versions")
      .withIndex("by_nep", (q) => q.eq("nep_name", args.nep_name))
      .order("desc")
      .take(1);
    return versions[0] ?? null;
  },
});

export const listByNep = query({
  args: { nep_name: v.string(), limit: v.optional(v.number()) },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("nep_versions")
      .withIndex("by_nep", (q) => q.eq("nep_name", args.nep_name))
      .order("desc")
      .take(args.limit ?? 20);
  },
});

export const getHistory = query({
  args: { limit: v.optional(v.number()) },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("nep_versions")
      .order("desc")
      .take(args.limit ?? 50);
  },
});
