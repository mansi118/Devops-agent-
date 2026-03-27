const axios = require("axios");

const STAKPAK_URL = process.env.STAKPAK_URL || "http://localhost:8765";
const ALLOWED_APPROVERS = (process.env.ALLOWED_APPROVERS || "").split(",").filter(Boolean);
const APPROVAL_TIMEOUT_MS = 30 * 60 * 1000; // 30 minutes

async function handleApprove({ ack, action, body, client }, logger) {
  await ack();

  const payload = JSON.parse(action.value);
  const approver = body.user.id;
  const messageTs = body.message.ts;
  const channel = body.channel.id;

  logger.info("Deployment approved", { approver, payload });

  // Check approver role (if configured)
  if (ALLOWED_APPROVERS.length > 0 && !ALLOWED_APPROVERS.includes(approver)) {
    await client.chat.postEphemeral({
      channel,
      user: approver,
      text: "You are not authorized to approve deployments.",
    });
    return;
  }

  // Update the approval message
  await client.chat.update({
    channel,
    ts: messageTs,
    text: `Deployment approved by <@${approver}>`,
    blocks: [
      {
        type: "section",
        text: {
          type: "mrkdwn",
          text: `*${payload.action === "rollback" ? "Rollback" : "Deployment"} Approved*\n\n` +
            `Environment: \`${payload.env}\`\n` +
            (payload.service ? `Service: \`${payload.service}\`\n` : "") +
            `Approved by: <@${approver}>\n` +
            `Time: ${new Date().toISOString()}`,
        },
      },
    ],
  });

  // Execute the approved action
  try {
    if (payload.action === "rollback") {
      await axios.post(`${STAKPAK_URL}/mcp/invoke`, {
        tool: "stakpak_deploy",
        input: {
          target: `${payload.env}.neuraledge.in`,
          strategy: "rollback",
          approval_source: "slack",
          approver,
        },
      });
    } else {
      await axios.post(`${STAKPAK_URL}/mcp/invoke`, {
        tool: "stakpak_deploy",
        input: {
          target: `${payload.env}.neuraledge.in`,
          service: payload.service,
          strategy: payload.env === "production" ? "canary" : "rolling",
          approval_source: "slack",
          approver,
        },
      });
    }

    await client.chat.postMessage({
      channel: process.env.DEPLOY_CHANNEL || "#deployments",
      text: `${payload.action === "rollback" ? "Rollback" : "Deployment"} to \`${payload.env}\` initiated (approved by <@${approver}>).`,
    });
  } catch (error) {
    logger.error(`Approved action failed: ${error.message}`);
    await client.chat.postMessage({
      channel,
      text: `Action execution failed: ${error.message}`,
    });
  }
}

async function handleReject({ ack, action, body, client }, logger) {
  await ack();

  const payload = JSON.parse(action.value);
  const rejector = body.user.id;
  const messageTs = body.message.ts;
  const channel = body.channel.id;

  logger.info("Deployment rejected", { rejector, payload });

  await client.chat.update({
    channel,
    ts: messageTs,
    text: `Deployment rejected by <@${rejector}>`,
    blocks: [
      {
        type: "section",
        text: {
          type: "mrkdwn",
          text: `*${payload.action === "rollback" ? "Rollback" : "Deployment"} Rejected*\n\n` +
            `Environment: \`${payload.env}\`\n` +
            `Rejected by: <@${rejector}>\n` +
            `Time: ${new Date().toISOString()}`,
        },
      },
    ],
  });

  // Notify requester
  if (payload.requester) {
    await client.chat.postMessage({
      channel: payload.requester,
      text: `Your ${payload.action === "rollback" ? "rollback" : "deployment"} request for \`${payload.env}\` was rejected by <@${rejector}>.`,
    });
  }
}

module.exports = { handleApprove, handleReject };
