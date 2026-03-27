# Ops NEop — NeuralEDGE Autonomous DevOps Agent

> **Version:** 1.0 | **Author:** ML (Yatharth Garg) | **Classification:** Confidential — Internal Use Only

Ops is NeuralEDGE's autonomous DevOps agent — a first-class NEop within the NEOS ecosystem. It eliminates the infrastructure management bottleneck by providing 24/7 monitoring, intelligent CI/CD, automated incident response, and self-improving deployment protocols.

---

## Architecture

```
                    ┌──────────────┐
                    │   GitHub     │
                    │  (Webhooks)  │
                    └──────┬───────┘
                           │
                           ▼
┌──────────┐     ┌─────────────────┐     ┌──────────────────┐
│  Slack   │◄───►│   n8n Engine    │◄───►│  Ops NEop Agent  │
│  Bot     │     │  (Orchestrator) │     │  (Stakpak Core)  │
└──────────┘     └─────────────────┘     └────────┬─────────┘
                                                   │
                    ┌──────────────────────────────┤
                    │                              │
                    ▼                              ▼
          ┌─────────────────┐          ┌──────────────────┐
          │  LLM Reasoning  │          │  MCP Tool Bus    │
          │  Claude + GLM-5 │          │  (60+ tools)     │
          └─────────────────┘          └────────┬─────────┘
                                                │
                 ┌──────────────┬───────────────┼───────────────┐
                 ▼              ▼               ▼               ▼
          ┌───────────┐ ┌───────────┐ ┌──────────────┐ ┌────────────┐
          │   AWS     │ │  Docker   │ │  Context     │ │   Other    │
          │  (EC2,S3) │ │  (ECR)    │ │  Vault       │ │   NEops    │
          └───────────┘ └───────────┘ └──────────────┘ └────────────┘
```

**Built on:**
- **[Stakpak](https://stakpak.dev)** (Rust, Apache 2.0) — forked as the agent runtime with enterprise-grade secret management and guardrails
- **n8n** (n8n.neuraledge.in) — workflow engine for visual CI/CD pipeline orchestration
- **Claude API** — primary LLM for failure investigation, code analysis, and IaC generation
- **MCP Protocol** — standard interface connecting Ops to all other NEops in the NEOS stack

---

## Target Outcomes (3 months)

| Metric | Current | Target |
|--------|---------|--------|
| Deployment Frequency | ~2/week | Daily |
| Lead Time for Changes | ~3 days | < 1 day |
| Change Failure Rate | ~20% | < 5% |
| Mean Time to Recovery | ~4 hours | < 30 minutes |

---

## Repository Structure

```
devops-agent/
├── agent/                    # Stakpak fork (Rust agent runtime)
├── config/                   # Stakpak configuration
│   ├── config.toml           # Main config with 4 profiles
│   ├── mcp.toml              # 12 MCP server connections
│   ├── profiles/             # Detailed profile configs (monitoring, deploy, incident)
│   ├── warden/               # Cedar guardrail policies (common, production, staging)
│   ├── prometheus.yml        # Prometheus scrape config
│   └── alert_rules.yml       # Prometheus alerting rules
├── neps/                     # Self-improving DevOps protocols (NePs)
│   ├── deploy.md             # Deployment with risk scoring & canary
│   ├── rollback.md           # Rollback decision protocol
│   ├── incident-response.md  # Incident detection → investigation → remediation
│   ├── security-scan.md      # CVE scanning, secret detection, TLS monitoring
│   ├── cost-optimize.md      # AWS cost analysis and optimization
│   ├── test-selection.md     # AI-driven test selection
│   └── changelog/            # NeP version history
├── n8n-workflows/            # n8n workflow JSON exports
│   ├── cicd-pipeline.json    # Full CI/CD pipeline
│   ├── health-check.json     # 5-min health checks
│   ├── incident-response.json
│   ├── daily-audit.json      # Security + dependency audit
│   ├── weekly-cost-report.json
│   └── daily-briefing.json   # Morning briefing for ML
├── convex/                   # Context Vault (Convex) schema + functions
│   ├── schema.ts             # Tables: deployments, incidents, nep_versions, audit_log
│   ├── deployments.ts        # Deployment CRUD + stats
│   ├── incidents.ts          # Incident CRUD + stats
│   ├── nep_versions.ts       # NeP version tracking
│   ├── audit_log.ts          # Immutable audit trail
│   └── search.ts             # Vector similarity search (RAG)
├── terraform/                # Infrastructure as Code
│   ├── main.tf               # Root module
│   └── modules/              # ECR, S3, Secrets, Monitoring, EC2
├── slack-bot/                # Slack bot (Bolt.js)
│   ├── app.js                # Main app with socket mode
│   ├── commands/             # /ops deploy, rollback, status, cost
│   └── handlers/             # Approval buttons, alert formatting
├── tests/                    # Test suites
│   ├── unit/                 # Risk scoring, test selection, NeP parser
│   ├── integration/          # Webhooks, staging deploy, MCP connections
│   └── e2e/                  # Full pipeline, incident response
├── scripts/                  # Helper scripts
│   ├── install.sh            # One-command installation
│   ├── setup-mcp.sh          # MCP connection verification
│   ├── import-n8n-workflows.sh
│   ├── seed-context-vault.py
│   └── health-check.sh
├── dashboards/               # Grafana dashboards (DORA, pipeline, cost)
├── docs/                     # Runbooks, onboarding, troubleshooting
├── docker-compose.yml        # Local development
├── docker-compose.prod.yml   # Production
├── Makefile                  # Common commands
└── CLAUDE.md                 # Claude Code configuration
```

---

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ and Python 3.10+
- AWS CLI configured
- GitHub and Slack access

### Installation

```bash
# Clone
git clone https://github.com/mansi118/Devops-agent-.git
cd Devops-agent-

# Configure
cp .env.example .env
# Fill in your API keys in .env

# Install
bash scripts/install.sh

# Start monitoring mode
make start
```

### Verify

```bash
# Check all services
bash scripts/health-check.sh

# Verify MCP connections
bash scripts/setup-mcp.sh

# Run tests
make test
```

---

## Core Components

### 1. Pipeline Monitor
Watches GitHub Actions across all repos. On failure: fetches logs → queries past incidents (RAG) → performs root cause analysis → auto-retries transient failures or creates detailed issues.

### 2. Deployment Engine
Full CI/CD lifecycle with AI-enhanced stages:

```
Git Push → AI Risk Triage → Smart Build → AI Test Selection → Security Scan
    → Staging (auto) → Canary (5-10%) → Production (approved)
```

- **Risk scoring** (1-10): Files changed, complexity, blast radius, past failure history
- **AI test selection**: Run 28% of tests on average (vs 100%), 0 false negatives target
- **Canary deploys**: 15-min observation, auto-rollback on metric degradation

### 3. Infrastructure Agent
Manages AWS infrastructure via Terraform: IaC generation, drift detection (every 6h), cost optimization, health checks (every 5min).

### 4. Security Sentinel
Continuous scanning: container images (Snyk), dependencies, secrets (trufflehog), TLS certificates (auto-renew), AWS security groups.

### 5. Incident Responder
Alert → classify severity → investigate → auto-fix known patterns → escalate unknowns. Escalation: Slack (5min) → WhatsApp (15min) → Phone (30min).

### 6. Optimization Engine
Self-improving loop: every deployment teaches Ops to deploy better. Adjusts risk scores, test selection, canary duration, build caching, and rollback thresholds.

---

## Profiles & Security

| Profile | Autonomy | Use Case |
|---------|----------|----------|
| `monitoring` | Full (read-only) | Health checks, log analysis, metric queries |
| `deploy` | Semi | CI/CD pipeline — staging auto, production needs Slack approval |
| `incident` | Semi | Emergency response — can restart services, rollback |
| `admin` | Full (MFA required) | Manual operations for ML/Shivam only |

### Security Layers

1. **Secret Substitution** — LLM never sees raw credentials (210+ secret types detected)
2. **Warden Guardrails** — Cedar policies block destructive operations (`rm -rf`, `DROP DATABASE`, etc.)
3. **Immutable Audit Trail** — Every action logged to S3 (WORM, 1-year retention)
4. **Role-Based Profiles** — Per-profile tool restrictions and approval requirements

---

## NePs (Self-Improving Protocols)

NePs are self-improving Skill.md-like files that track their own performance and auto-adjust:

```markdown
# NeuralEDGE Protocol: Deployment

## Metrics (auto-updated)
- success_rate: 94%
- avg_deploy_time: 4m 32s
- rollback_rate: 6.4%

## Decision Rules
IF risk_score < 5: auto-deploy with canary
IF risk_score >= 8: block, require senior approval

## Self-Optimization Rules
- Calibrate risk scores against actual outcomes
- Adjust canary duration based on pass/fail patterns
- Tune rollback thresholds to minimize false positives
```

---

## NEOS Integration

Ops connects to every other NEop in the NEOS ecosystem via MCP:

| NEop | Integration |
|------|-------------|
| **Forge** | Receives build artifacts, triggers code review on IaC changes |
| **Scout** | Gets CVE research, requests infrastructure pattern analysis |
| **Axe** | Sends deployment data for changelog generation |
| **Aria** | On-call schedule, team availability |
| **Recon** | Infrastructure status for client demos |
| **Emma** | WhatsApp alerts on client-facing outages |
| **Chief of Staff** | Daily infrastructure briefing data |

---

## Commands

### Makefile

```bash
make install          # Install Stakpak
make setup            # Configure all connections
make start            # Start monitoring mode
make stop             # Stop the agent
make status           # Check agent status
make test             # Run all tests
make deploy-staging   # Deploy to staging
make deploy-production # Deploy to production (with approval)
make cost-report      # Generate AWS cost report
make health           # Run health checks
```

### Slack

```
/ops deploy <env> <service>   — Deploy a service
/ops rollback <env>           — Rollback last deployment
/ops status                   — System status overview
/ops cost-report              — AWS cost analysis
```

---

## Rollout Plan (4 Weeks)

| Week | Focus | Key Milestone |
|------|-------|---------------|
| **1** | Foundation | Stakpak running 24/7, Slack alerts firing, zero false alerts for 48h |
| **2** | Intelligence | AI failure investigation, 5+ staging deploys, RAG retrieval working |
| **3** | Automation | Canary deploys, auto-rollback, security scanning, DORA dashboard live |
| **4** | Full Autonomy | Production pipeline, NEop integration, self-optimization loop active |

---

## Cost Analysis

| Additional Cost | Monthly |
|----------------|---------|
| Claude API (~100 calls/day) | ~₹5,000 |
| AWS S3 (audit logs) | ~₹500 |
| Other services | ~₹2,000 |
| **Total** | **~₹7,500** |

| Expected Savings | Monthly |
|-----------------|---------|
| Engineer time recovered (12h/week) | ₹75,000 |
| Faster incident resolution | ₹25,000 |
| AWS resource optimization | ₹50,000+ |
| Reduced deployment failures | ₹15,000 |
| **Total** | **₹1,65,000+** |

**ROI: 22x return** on the ₹7,500/month investment.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Agent Engine | Stakpak (Rust, Apache 2.0) |
| Orchestration | n8n |
| LLM (Primary) | Claude API (Sonnet 4) |
| LLM (Fallback) | ZAI/GLM-5 (local) |
| Agent Protocol | MCP v1.0 |
| Context Store | Convex (vector search) |
| Cloud | AWS (ap-south-1, Mumbai) |
| IaC | Terraform |
| Containers | Docker + AWS ECR |
| Monitoring | Prometheus + Grafana |
| Secrets | AWS Secrets Manager |
| Security Scanning | Snyk + trufflehog |

---

## License

Confidential — NeuralEDGE Internal Use Only

---

*NeuralEDGE · Your AI Partners · neuraledge.in*
