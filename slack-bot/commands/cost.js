const axios = require("axios");

const STAKPAK_URL = process.env.STAKPAK_URL || "http://localhost:8765";

async function handle({ command, params, respond, client, logger }) {
  logger.info("Cost report requested", { user: command.user_id });

  await respond("Generating cost optimization report... This may take a minute.");

  try {
    const result = await axios.post(`${STAKPAK_URL}/mcp/invoke`, {
      tool: "stakpak_analyze",
      input: {
        prompt:
          "Analyze all NeuralEDGE AWS resources. Find idle EC2 instances, orphaned EBS volumes, " +
          "unused Elastic IPs, over-provisioned RDS. Calculate potential savings. " +
          "Format as a concise Slack message with top 3 recommendations.",
        tools: ["ec2_list", "ec2_describe", "cloudwatch_query", "s3_list", "rds_describe"],
      },
    });

    await client.chat.postMessage({
      channel: process.env.METRICS_CHANNEL || "#eng-metrics",
      text: "Cost Optimization Report",
      blocks: [
        {
          type: "header",
          text: { type: "plain_text", text: "AWS Cost Optimization Report" },
        },
        {
          type: "section",
          text: {
            type: "mrkdwn",
            text: result.data?.report || "Report generated. Check Notion for full details.",
          },
        },
        {
          type: "context",
          elements: [
            {
              type: "mrkdwn",
              text: `Requested by <@${command.user_id}> | ${new Date().toISOString()}`,
            },
          ],
        },
      ],
    });

    await respond("Cost report posted to #eng-metrics.");
  } catch (error) {
    logger.error(`Cost report failed: ${error.message}`);
    await respond(`Cost report generation failed: ${error.message}`);
  }
}

module.exports = { handle };
