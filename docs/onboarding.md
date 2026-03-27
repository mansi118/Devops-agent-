# Ops NEop — Engineer Onboarding Guide

## Prerequisites
- Docker and Docker Compose installed
- Node.js 18+ and Python 3.10+
- AWS CLI configured with NeuralEDGE credentials
- GitHub access to neuraledge org
- Slack workspace access

## Setup Steps

### 1. Clone and Install
```bash
git clone https://github.com/neuraledge/ops-neop.git
cd ops-neop
cp .env.example .env
# Fill in your credentials in .env
bash scripts/install.sh
```

### 2. Start Local Environment
```bash
make start  # Starts Stakpak, Prometheus, Grafana
```

### 3. Verify
```bash
bash scripts/health-check.sh
bash scripts/setup-mcp.sh
```

## Key Concepts

### NePs (NeuralEDGE Protocols)
Self-improving markdown files in `neps/`. They define decision rules, track their own metrics, and auto-optimize based on outcomes. See `neps/deploy.md` for the canonical example.

### Profiles
Stakpak profiles control what the agent can do:
- **monitoring**: Read-only, health checks
- **deploy**: Build, test, deploy (staging auto, prod needs approval)
- **incident**: Can restart services, rollback
- **admin**: Full access, requires MFA

### Warden Guardrails
Cedar policies in `config/warden/` that prevent destructive actions. Production changes always require Slack approval.

## Common Commands
```bash
make start          # Start monitoring mode
make status         # Check agent status
make test           # Run all tests
make deploy-staging # Deploy to staging
make health         # Run health checks
```

## Architecture
- `agent/` — Stakpak fork (Rust agent runtime)
- `config/` — All configuration (profiles, MCP, Warden)
- `neps/` — Self-improving protocols
- `n8n-workflows/` — Visual pipeline definitions
- `convex/` — Context Vault (deployment history, incidents)
- `terraform/` — Infrastructure as Code
- `slack-bot/` — Slack command interface
