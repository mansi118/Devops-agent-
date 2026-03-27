#!/usr/bin/env bash
set -euo pipefail

N8N_URL="${N8N_URL:-https://n8n.neuraledge.in}"
N8N_API_KEY="${N8N_API_KEY:-}"
WORKFLOW_DIR="$(dirname "$0")/../n8n-workflows"

echo "============================================"
echo "  Ops NEop — Import n8n Workflows"
echo "============================================"

if [ -z "$N8N_API_KEY" ]; then
    echo "ERROR: N8N_API_KEY not set. Export it and re-run."
    exit 1
fi

for workflow in "$WORKFLOW_DIR"/*.json; do
    name=$(basename "$workflow" .json)
    echo "Importing: $name..."

    response=$(curl -sf -X POST "$N8N_URL/api/v1/workflows" \
        -H "X-N8N-API-KEY: $N8N_API_KEY" \
        -H "Content-Type: application/json" \
        -d @"$workflow" 2>&1) || {
        echo "  WARN: Failed to import $name (may already exist). Trying update..."
        # Try to find and update existing workflow
        existing=$(curl -sf "$N8N_URL/api/v1/workflows" \
            -H "X-N8N-API-KEY: $N8N_API_KEY" | \
            python3 -c "import sys,json; data=json.load(sys.stdin); print(next((w['id'] for w in data.get('data',[]) if '${name}' in w.get('name','')), ''))" 2>/dev/null || echo "")

        if [ -n "$existing" ]; then
            curl -sf -X PATCH "$N8N_URL/api/v1/workflows/$existing" \
                -H "X-N8N-API-KEY: $N8N_API_KEY" \
                -H "Content-Type: application/json" \
                -d @"$workflow" >/dev/null && echo "  Updated: $name" || echo "  FAIL: $name"
        else
            echo "  SKIP: Could not find existing workflow to update"
        fi
        continue
    }

    echo "  OK: $name imported"
done

echo ""
echo "Done. Verify at: $N8N_URL"
