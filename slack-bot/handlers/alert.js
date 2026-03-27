const axios = require("axios");

const SEVERITY_CONFIG = {
  P1: { color: "#ff0000", emoji: ":rotating_light:", channel: "#ops-alerts" },
  P2: { color: "#ff9900", emoji: ":warning:", channel: "#ops-alerts" },
  P3: { color: "#ffcc00", emoji: ":information_source:", channel: "#ops-alerts" },
};

async function sendAlert(client, { severity, title, description, service, incident_id, investigation }, logger) {
  const config = SEVERITY_CONFIG[severity] || SEVERITY_CONFIG.P3;

  const blocks = [
    {
      type: "header",
      text: { type: "plain_text", text: `${config.emoji} ${severity} — ${title}` },
    },
    {
      type: "section",
      fields: [
        { type: "mrkdwn", text: `*Service:*\n${service}` },
        { type: "mrkdwn", text: `*Severity:*\n${severity}` },
        { type: "mrkdwn", text: `*Incident ID:*\n${incident_id}` },
        { type: "mrkdwn", text: `*Time:*\n${new Date().toISOString()}` },
      ],
    },
    {
      type: "section",
      text: { type: "mrkdwn", text: `*Description:*\n${description}` },
    },
  ];

  if (investigation) {
    blocks.push({
      type: "section",
      text: { type: "mrkdwn", text: `*Investigation:*\n${investigation}` },
    });
  }

  blocks.push({
    type: "actions",
    elements: [
      {
        type: "button",
        text: { type: "plain_text", text: "Acknowledge" },
        action_id: "incident_acknowledge",
        value: JSON.stringify({ incident_id, severity }),
      },
      {
        type: "button",
        text: { type: "plain_text", text: "Escalate" },
        style: "danger",
        action_id: "incident_escalate",
        value: JSON.stringify({ incident_id, severity }),
      },
    ],
  });

  await client.chat.postMessage({
    channel: config.channel,
    text: `${severity} Alert: ${title}`,
    blocks,
    attachments: [{ color: config.color }],
  });

  logger.info(`Alert sent: ${severity} - ${title}`, { incident_id, service });
}

async function handleAcknowledge({ ack, action, body, client }, logger) {
  await ack();

  const payload = JSON.parse(action.value);
  const user = body.user.id;

  logger.info("Incident acknowledged", { user, incident_id: payload.incident_id });

  await client.chat.update({
    channel: body.channel.id,
    ts: body.message.ts,
    text: `Incident ${payload.incident_id} acknowledged by <@${user}>`,
    blocks: [
      ...body.message.blocks.slice(0, -1),
      {
        type: "context",
        elements: [
          { type: "mrkdwn", text: `Acknowledged by <@${user}> at ${new Date().toISOString()}` },
        ],
      },
    ],
  });
}

async function handleEscalate({ ack, action, body, client }, logger) {
  await ack();

  const payload = JSON.parse(action.value);
  const user = body.user.id;

  logger.info("Incident escalated", { user, incident_id: payload.incident_id });

  // Escalate via WhatsApp for P1
  if (payload.severity === "P1") {
    try {
      const STAKPAK_URL = process.env.STAKPAK_URL || "http://localhost:8765";
      await axios.post(`${STAKPAK_URL}/mcp/invoke`, {
        tool: "whatsapp_alert",
        input: {
          contacts: ["shivam", "ankit", "ml"],
          message: `P1 INCIDENT ESCALATED: ${payload.incident_id}. Check #ops-alerts for details.`,
        },
      });
    } catch (error) {
      logger.error(`WhatsApp escalation failed: ${error.message}`);
    }
  }

  await client.chat.postMessage({
    channel: body.channel.id,
    text: `Incident ${payload.incident_id} escalated by <@${user}>. On-call team notified.`,
  });
}

module.exports = { sendAlert, handleAcknowledge, handleEscalate };
