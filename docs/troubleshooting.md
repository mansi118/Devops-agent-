# Ops NEop — Troubleshooting Guide

## Stakpak Won't Start
- Check `STAKPAK_API_KEY` and `ANTHROPIC_API_KEY` are set
- Verify Docker is running: `docker info`
- Check port 8765 is free: `lsof -i :8765`
- Check logs: `docker compose logs stakpak`

## MCP Connection Failures
- Run `bash scripts/setup-mcp.sh` to test all connections
- Verify environment variables for each service
- Check if the MCP server process is running
- For HTTP-based servers, verify the URL is accessible

## Slack Bot Not Responding
- Verify `SLACK_BOT_TOKEN` and `SLACK_APP_TOKEN` are set
- Check socket mode is enabled in Slack App settings
- Check bot health: `curl http://localhost:3001/health`
- Check logs: `docker compose logs slack-bot`

## Pipeline Stuck
- Check n8n workflow status at n8n.neuraledge.in
- Look for pending Slack approvals in #ops-approvals
- Check if Docker build is hanging (resource limits?)
- Verify ECR push permissions

## False Alerts
- Check Prometheus alert rules in `config/alert_rules.yml`
- Adjust thresholds if too sensitive
- Review alert history in Grafana
- Update NeP self-optimization rules to adjust detection

## Context Vault Issues
- Verify Convex deployment URL and API key
- Check Convex dashboard for function errors
- Run `python3 scripts/seed-context-vault.py` to test connectivity

## Tests Failing
- Install test deps: `pip install -r tests/requirements.txt`
- Run unit tests only: `pytest tests/unit/ -v`
- Check if fixtures match current schema
