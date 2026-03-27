import { v } from "convex/values";
import { action } from "./_generated/server";

export const similarDeployments = action({
  args: {
    embedding: v.array(v.float64()),
    status: v.optional(v.union(v.literal("success"), v.literal("failed"), v.literal("rolled_back"))),
    neop: v.optional(v.string()),
    limit: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    const filter: Record<string, string> = {};
    if (args.status) filter.status = args.status;
    if (args.neop) filter.neop = args.neop;

    const results = await ctx.vectorSearch("deployments", "by_embedding", {
      vector: args.embedding,
      limit: args.limit ?? 5,
      filter: Object.keys(filter).length > 0
        ? (q: any) => {
            let f = q;
            if (args.status) f = f.eq("status", args.status);
            if (args.neop) f = f.eq("neop", args.neop);
            return f;
          }
        : undefined,
    });

    return results;
  },
});

export const similarIncidents = action({
  args: {
    embedding: v.array(v.float64()),
    severity: v.optional(v.union(v.literal("P1"), v.literal("P2"), v.literal("P3"))),
    service: v.optional(v.string()),
    limit: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    const results = await ctx.vectorSearch("incidents", "by_embedding", {
      vector: args.embedding,
      limit: args.limit ?? 5,
      filter: args.severity
        ? (q: any) => q.eq("severity", args.severity)
        : args.service
          ? (q: any) => q.eq("service", args.service)
          : undefined,
    });

    return results;
  },
});
