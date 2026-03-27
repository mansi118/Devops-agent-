.PHONY: install setup start stop status test deploy-staging deploy-production cost-report health

install:
	curl -sSL https://stakpak.dev/install.sh | sh
	stakpak login --api-key $$STAKPAK_API_KEY

setup:
	cp config/config.toml ~/.stakpak/config.toml
	cp config/mcp.toml ~/.stakpak/mcp.toml
	bash scripts/setup-mcp.sh
	bash scripts/import-n8n-workflows.sh
	python3 scripts/seed-context-vault.py

start:
	stakpak autopilot up --profile monitoring

stop:
	stakpak autopilot down

status:
	stakpak autopilot status

test:
	pytest tests/unit/ -v
	pytest tests/integration/ -v

deploy-staging:
	stakpak --async "Deploy the latest main branch to staging using the deploy NeP"

deploy-production:
	stakpak --async "Deploy the latest production branch with canary strategy. Request Slack approval."

cost-report:
	stakpak --async "Generate a cost optimization report for all NeuralEDGE AWS resources"

health:
	stakpak --async "Run comprehensive health check on all services and report to Slack"
