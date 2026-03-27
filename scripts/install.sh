#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo "============================================"
echo "  NeuralEDGE Ops NEop — Installation"
echo "============================================"

# Check prerequisites
log_info "Checking prerequisites..."
missing=()
command -v docker >/dev/null 2>&1 || missing+=("docker")
command -v git >/dev/null 2>&1 || missing+=("git")
command -v curl >/dev/null 2>&1 || missing+=("curl")
command -v node >/dev/null 2>&1 || missing+=("node")
command -v python3 >/dev/null 2>&1 || missing+=("python3")

if [ ${#missing[@]} -gt 0 ]; then
    log_error "Missing: ${missing[*]}"
    exit 1
fi
log_info "All prerequisites found."

# Check env vars
log_info "Checking environment..."
for var in ANTHROPIC_API_KEY GITHUB_TOKEN SLACK_BOT_TOKEN; do
    if [ -z "${!var:-}" ]; then
        log_warn "Missing: $var"
    fi
done

# Install Stakpak
if ! command -v stakpak >/dev/null 2>&1; then
    log_info "Installing Stakpak..."
    curl -sSL https://stakpak.dev/install.sh | sh
fi

# Configure
log_info "Configuring Stakpak..."
mkdir -p "$HOME/.stakpak/rulebooks"
cp "$PROJECT_DIR/config/config.toml" "$HOME/.stakpak/config.toml"
cp "$PROJECT_DIR/config/mcp.toml" "$HOME/.stakpak/mcp.toml"
cp "$PROJECT_DIR/neps/"*.md "$HOME/.stakpak/rulebooks/"

# Install Slack bot deps
if [ -d "$PROJECT_DIR/slack-bot" ]; then
    log_info "Installing Slack bot dependencies..."
    cd "$PROJECT_DIR/slack-bot" && npm install --production && cd "$PROJECT_DIR"
fi

# Create directories
sudo mkdir -p /var/log/ops-neop /opt/ops-neop 2>/dev/null || true

echo ""
log_info "Installation complete!"
echo "Next: bash scripts/setup-mcp.sh && make start"
