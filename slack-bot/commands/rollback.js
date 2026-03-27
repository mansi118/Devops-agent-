const axios = require("axios");

const STAKPAK_URL = process.env.STAKPAK_URL || "http://localhost:8765";

async function handle({ command, params, respond, client, logger }) {
  const env = params[0];

  if (!env) {
    return respond("Usage: `/ops rollback <env>`\nExample: `/ops rollback production`");
  }

  logger.info(`Rollback requested for ${env}`, { user: command.user_id });

  // Fetch last deployment info
  let lastDeploy;
  try {
    const result = await axios.post(`${STAKPAK_URL}/mcp/invoke`, {
      tool: "context_vault_query",
      input: { table: "deployments", filter: { environment: env }, limit: 1, order: "desc" },
    });
    lastDeploy = result.data;
  } catch (error) {
    return respond(`Could not fetch last deployment: ${error.message}`);
  }

  // Always require approval for rollbacks
  await client.chat.postMessage({
    channel: process.env.APPROVAL_CHANNEL || "#ops-approvals",
    text: `Rollback requested for ${env}`,
    blocks: [
      {
        type: "section",
        text: {
          type: "mrkdwn",
          text: `*Rollback Request*\n\nEnvironment: \`${env}\`\nLast Deploy: \`${lastDeploy?.commit_sha?.substring(0, 7) || "unknown"}\`\nRequested by: <@${command.user_id}>`,
        },
      },
      {
        type: "actions",
        elements: [
          {
            type: "button",
            text: { type: "plain_text", text: "Approve Rollback" },
            style: "danger",
            action_id: "deployment_approve",
            value: JSON.stringify({ env, action: "rollback", requester: command.user_id }),
          },
          {
            type: "button",
            text: { type: "plain_text", text: "Cancel" },
            action_id: "deployment_reject",
            value: JSON.stringify({ env, action: "rollback", requester: command.user_id }),
          },
        ],
      },
    ],
  });

  await respond(`Rollback for \`${env}\` submitted for approval in #ops-approvals.`);
}

module.exports = { handle };
