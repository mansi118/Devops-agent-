const axios = require("axios");

const STAKPAK_URL = process.env.STAKPAK_URL || "http://localhost:8765";

async function handle({ command, params, respond, client, logger }) {
  logger.info("Status requested", { user: command.user_id });

  try {
    // Query health and deployment data
    const [healthResult, deployResult] = await Promise.allSettled([
      axios.post(`${STAKPAK_URL}/mcp/invoke`, {
        tool: "health_check",
        input: {
          endpoints: [
            { name: "NEOS API", url: "https://api.neuraledge.in/health" },
            { name: "n8n", url: "https://n8n.neuraledge.in/healthz" },
            { name: "OpenClaw", url: "http://13.233.60.59:3000/health" },
            { name: "Ops Agent", url: "http://localhost:8765/health" },
          ],
        },
      }),
      axios.post(`${STAKPAK_URL}/mcp/invoke`, {
        tool: "context_vault_query",
        input: { table: "deployments", limit: 5, order: "desc" },
      }),
    ]);

    const health = healthResult.status === "fulfilled" ? healthResult.value.data : null;
    const deploys = deployResult.status === "fulfilled" ? deployResult.value.data : [];

    const healthStatus = health
      ? health.checks
          .map((c) => `${c.status === "healthy" ? ":white_check_mark:" : ":x:"} ${c.name}`)
          .join("\n")
      : ":warning: Health data unavailable";

    const deployList = Array.isArray(deploys)
      ? deploys
          .slice(0, 5)
          .map(
            (d) =>
              `${d.status === "success" ? ":white_check_mark:" : ":x:"} \`${d.neop}\` → ${d.environment} (${d.commit_sha?.substring(0, 7)})`
          )
          .join("\n")
      : "No recent deployments";

    await respond({
      blocks: [
        {
          type: "header",
          text: { type: "plain_text", text: "Ops NEop — System Status" },
        },
        {
          type: "section",
          text: { type: "mrkdwn", text: `*Service Health*\n${healthStatus}` },
        },
        { type: "divider" },
        {
          type: "section",
          text: { type: "mrkdwn", text: `*Recent Deployments*\n${deployList}` },
        },
        {
          type: "context",
          elements: [
            {
              type: "mrkdwn",
              text: `Last updated: ${new Date().toISOString()}`,
            },
          ],
        },
      ],
    });
  } catch (error) {
    logger.error(`Status check failed: ${error.message}`);
    await respond(`Status check failed: ${error.message}`);
  }
}

module.exports = { handle };
