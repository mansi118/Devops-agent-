#!/usr/bin/env bash
set -euo pipefail

GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[1;33m'; NC='\033[0m'

echo "============================================"
echo "  Ops NEop — MCP Connection Verification"
echo "============================================"

check_endpoint() {
    local name="$1" url="$2"
    if curl -sf --max-time 5 "$url" >/dev/null 2>&1; then
        echo -e "  ${GREEN}[OK]${NC} $name ($url)"
        return 0
    else
        echo -e "  ${RED}[FAIL]${NC} $name ($url)"
        return 1
    fi
}

check_command() {
    local name="$1" cmd="$2"
    if command -v "$cmd" >/dev/null 2>&1; then
        echo -e "  ${GREEN}[OK]${NC} $name ($cmd found)"
        return 0
    else
        echo -e "  ${YELLOW}[WARN]${NC} $name ($cmd not found)"
        return 1
    fi
}

echo ""
echo "Checking MCP server connectivity..."
failed=0

check_endpoint "Prometheus" "http://localhost:9090/-/healthy" || ((failed++))
check_endpoint "Grafana" "http://localhost:3000/api/health" || ((failed++))
check_endpoint "Stakpak Agent" "http://localhost:8765/health" || ((failed++))
check_command "Docker" "docker" || ((failed++))
check_command "Terraform" "terraform" || ((failed++))
check_command "Node.js" "node" || ((failed++))

echo ""
echo "Checking environment variables..."
for var in ANTHROPIC_API_KEY GITHUB_TOKEN SLACK_BOT_TOKEN AWS_ACCESS_KEY_ID; do
    if [ -n "${!var:-}" ]; then
        echo -e "  ${GREEN}[OK]${NC} $var is set"
    else
        echo -e "  ${YELLOW}[WARN]${NC} $var is not set"
    fi
done

echo ""
if [ $failed -eq 0 ]; then
    echo -e "${GREEN}All MCP connections verified.${NC}"
else
    echo -e "${YELLOW}$failed connection(s) failed. Some features may be limited.${NC}"
fi
