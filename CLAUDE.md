# CLAUDE.md — Ops NEop Repository

## Project Context
This is the NeuralEDGE Ops NEop — an autonomous DevOps agent built on a Stakpak fork.
It manages CI/CD pipelines, infrastructure, security, and incident response for the NEOS platform.

## Tech Stack
- Stakpak (Rust) — agent runtime
- n8n — workflow orchestration
- Convex — Context Vault (deployment history, incidents)
- Claude API — LLM reasoning
- Docker + AWS — infrastructure
- MCP — inter-agent communication

## Key Files
- `config/mcp.toml` — MCP server connections
- `config/config.toml` — Stakpak profiles
- `config/warden/*.cedar` — security guardrail policies
- `neps/*.md` — self-improving DevOps protocols
- `n8n-workflows/*.json` — n8n workflow definitions
- `convex/schema.ts` — Context Vault database schema
- `terraform/` — infrastructure-as-code

## Conventions
- All infrastructure changes go through Terraform (never manual)
- Security policies in Cedar (config/warden/)
- NePs use the standard format with ## Metrics, ## Decision Rules, ## Self-Optimization, ## Changelog
- Commit messages follow conventional commits (feat:, fix:, chore:, docs:)
- All secrets managed via AWS Secrets Manager + Stakpak substitution

## Testing
- Unit tests: `pytest tests/unit/`
- Integration tests: `pytest tests/integration/`
- E2E tests: `pytest tests/e2e/` (requires running Stakpak instance)

## Deployment
- Staging: auto-deployed on push to main
- Production: canary + Slack approval on push to production
- Self-deploy: Ops deploys itself (dogfooding)
