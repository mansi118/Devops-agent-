#!/usr/bin/env bash
set -euo pipefail

GREEN='\033[0;32m'; RED='\033[0;31m'; NC='\033[0m'
failed=0

check() {
    local name="$1" url="$2"
    if curl -sf --max-time 5 "$url" >/dev/null 2>&1; then
        echo -e "${GREEN}[OK]${NC} $name"
    else
        echo -e "${RED}[FAIL]${NC} $name"
        ((failed++))
    fi
}

echo "Ops NEop — Health Check"
echo "======================="
check "Stakpak Agent"  "http://localhost:8765/health"
check "Prometheus"     "http://localhost:9090/-/healthy"
check "Grafana"        "http://localhost:3000/api/health"
check "Slack Bot"      "http://localhost:3001/health"
check "Node Exporter"  "http://localhost:9100/metrics"

echo ""
[ $failed -eq 0 ] && echo -e "${GREEN}All services healthy.${NC}" && exit 0
echo -e "${RED}$failed service(s) unhealthy.${NC}" && exit 1
