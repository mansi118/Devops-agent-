const { App } = require("@slack/bolt");
const winston = require("winston");
require("dotenv").config({ path: "../.env" });

const deployCmd = require("./commands/deploy");
const rollbackCmd = require("./commands/rollback");
const statusCmd = require("./commands/status");
const costCmd = require("./commands/cost");
const approvalHandler = require("./handlers/approval");
const alertHandler = require("./handlers/alert");

// Logger
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || "info",
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({ filename: "/var/log/ops-neop/slack-bot.log" }),
  ],
});

// Initialize Bolt app
const app = new App({
  token: process.env.SLACK_BOT_TOKEN,
  appToken: process.env.SLACK_APP_TOKEN,
  socketMode: true,
  logLevel: "info",
});

// Register slash commands
app.command("/ops", async ({ command, ack, respond, client }) => {
  await ack();

  const args = command.text.trim().split(/\s+/);
  const subcommand = args[0] || "help";
  const params = args.slice(1);

  logger.info(`Command received: /ops ${command.text}`, {
    user: command.user_id,
    channel: command.channel_id,
  });

  try {
    switch (subcommand) {
      case "deploy":
        await deployCmd.handle({ command, params, respond, client, logger });
        break;
      case "rollback":
        await rollbackCmd.handle({ command, params, respond, client, logger });
        break;
      case "status":
        await statusCmd.handle({ command, params, respond, client, logger });
        break;
      case "cost":
      case "cost-report":
        await costCmd.handle({ command, params, respond, client, logger });
        break;
      case "help":
      default:
        await respond({
          blocks: [
            {
              type: "section",
              text: {
                type: "mrkdwn",
                text: "*Ops NEop Commands*\n\n" +
                  "`/ops deploy <env> <service>` — Deploy a service\n" +
                  "`/ops rollback <env>` — Rollback last deployment\n" +
                  "`/ops status` — System status overview\n" +
                  "`/ops cost-report` — AWS cost analysis\n" +
                  "`/ops help` — Show this message",
              },
            },
          ],
        });
    }
  } catch (error) {
    logger.error(`Command failed: ${error.message}`, { error });
    await respond(`Error: ${error.message}`);
  }
});

// Register approval action handlers
app.action("deployment_approve", async (args) => {
  await approvalHandler.handleApprove(args, logger);
});

app.action("deployment_reject", async (args) => {
  await approvalHandler.handleReject(args, logger);
});

app.action("incident_acknowledge", async (args) => {
  await alertHandler.handleAcknowledge(args, logger);
});

app.action("incident_escalate", async (args) => {
  await alertHandler.handleEscalate(args, logger);
});

// Health check endpoint
const http = require("http");
const healthServer = http.createServer((req, res) => {
  if (req.url === "/health" || req.url === "/metrics") {
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ status: "healthy", uptime: process.uptime() }));
  } else {
    res.writeHead(404);
    res.end();
  }
});

// Start
(async () => {
  await app.start();
  healthServer.listen(3001);
  logger.info("Ops NEop Slack Bot is running (socket mode + health on :3001)");
})();

// Graceful shutdown
process.on("SIGTERM", async () => {
  logger.info("Shutting down...");
  healthServer.close();
  await app.stop();
  process.exit(0);
});

process.on("SIGINT", async () => {
  logger.info("Shutting down...");
  healthServer.close();
  await app.stop();
  process.exit(0);
});
