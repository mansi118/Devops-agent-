const axios = require("axios");

const STAKPAK_URL = process.env.STAKPAK_URL || "http://localhost:8765";
const VALID_ENVS = ["staging", "production"];

async function handle({ command, params, respond, client, logger }) {
  const env = params[0];
  const service = params[1];

  if (!env || !service) {
    return respond("Usage: `/ops deploy <env> <service>`\nExample: `/ops deploy staging neos-api`");
  }

  if (!VALID_ENVS.includes(env)) {
    return respond(`Invalid environment: \`${env}\`. Must be one of: ${VALID_ENVS.join(", ")}`);
  }

  logger.info(`Deploy requested: ${service} to ${env}`, { user: command.user_id });

  if (env === "production") {
    // Production requires approval
    await client.chat.postMessage({
      channel: process.env.APPROVAL_CHANNEL || "#ops-approvals",
      text: `Production deployment requested for ${service}`,
      blocks: [
        {
          type: "section",
          text: {
            type: "mrkdwn",
            text: `*Production Deployment Request*\n\nService: \`${service}\`\nRequested by: <@${command.user_id}>\nTime: ${new Date().toISOString()}`,
          },
        },
        {
          type: "actions",
          elements: [
            {
              type: "button",
              text: { type: "plain_text", text: "Approve" },
              style: "primary",
              action_id: "deployment_approve",
              value: JSON.stringify({ env, service, requester: command.user_id }),
            },
            {
              type: "button",
              text: { type: "plain_text", text: "Reject" },
              style: "danger",
              action_id: "deployment_reject",
              value: JSON.stringify({ env, service, requester: command.user_id }),
            },
          ],
        },
      ],
    });

    await respond(`Production deployment for \`${service}\` submitted for approval in #ops-approvals.`);
  } else {
    // Staging: deploy directly
    await respond(`Deploying \`${service}\` to \`${env}\`...`);

    try {
      const result = await axios.post(`${STAKPAK_URL}/mcp/invoke`, {
        tool: "stakpak_deploy",
        input: {
          target: `${env}.neuraledge.in`,
          service,
          strategy: "rolling",
        },
      });

      await client.chat.postMessage({
        channel: process.env.DEPLOY_CHANNEL || "#deployments",
        text: `Deployment of \`${service}\` to \`${env}\` completed successfully.`,
        blocks: [
          {
            type: "section",
            text: {
              type: "mrkdwn",
              text: `*Deployment Complete*\n\nService: \`${service}\`\nEnvironment: \`${env}\`\nStatus: Success\nTriggered by: <@${command.user_id}>`,
            },
          },
        ],
      });
    } catch (error) {
      logger.error(`Deploy failed: ${error.message}`);
      await respond(`Deployment failed: ${error.message}`);
    }
  }
}

module.exports = { handle };
