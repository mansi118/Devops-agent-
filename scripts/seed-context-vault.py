#!/usr/bin/env python3
"""Seed the Convex Context Vault with sample data for development/demo."""

import os
import json
import time
import random
import httpx

CONVEX_URL = os.environ.get("CONVEX_DEPLOYMENT_URL", "")
CONVEX_KEY = os.environ.get("CONVEX_API_KEY", "")

SAMPLE_DEPLOYMENTS = [
    {
        "deployment_id": f"deploy-{i:03d}",
        "neop": random.choice(["neos-api", "aria", "recon", "forge", "scout"]),
        "commit_sha": f"{random.randint(0, 0xFFFFFF):06x}{random.randint(0, 0xFFFFFF):06x}",
        "branch": "main",
        "environment": random.choice(["staging", "production"]),
        "status": random.choices(["success", "failed", "rolled_back"], weights=[85, 10, 5])[0],
        "risk_score": random.randint(1, 8),
        "actual_outcome": "clean",
        "duration_ms": random.randint(120000, 600000),
        "test_count": random.randint(20, 100),
        "test_total": 400,
        "build_cache_hit_rate": round(random.uniform(0.6, 0.95), 2),
        "metrics": {
            "error_rate": round(random.uniform(0, 0.03), 4),
            "latency_p99_ms": random.randint(100, 500),
            "cpu_percent": random.randint(20, 70),
            "memory_percent": random.randint(30, 80),
        },
        "embedding": [0.0] * 1536,
        "timestamp": int(time.time() * 1000) - random.randint(0, 30 * 86400 * 1000),
    }
    for i in range(10)
]

SAMPLE_INCIDENTS = [
    {
        "incident_id": f"INC-{i:03d}",
        "severity": random.choice(["P1", "P2", "P3"]),
        "service": random.choice(["neos-api", "n8n", "openclaw"]),
        "alert_source": random.choice(["prometheus", "cloudwatch", "health_check"]),
        "root_cause": random.choice([
            "Connection pool exhausted",
            "OOM killed",
            "Disk space critical",
            "TLS certificate expired",
            "High error rate after deploy",
        ]),
        "resolution": "Service restarted, root cause addressed",
        "time_to_detect_ms": random.randint(10000, 120000),
        "time_to_resolve_ms": random.randint(60000, 900000),
        "was_auto_resolved": random.choice([True, False]),
        "embedding": [0.0] * 1536,
        "timestamp": int(time.time() * 1000) - random.randint(0, 30 * 86400 * 1000),
    }
    for i in range(5)
]

def main():
    if not CONVEX_URL:
        print("CONVEX_DEPLOYMENT_URL not set. Printing sample data instead.")
        print(f"\nSample Deployments ({len(SAMPLE_DEPLOYMENTS)}):")
        for d in SAMPLE_DEPLOYMENTS[:2]:
            print(f"  {d['deployment_id']}: {d['neop']} -> {d['environment']} ({d['status']})")
        print(f"\nSample Incidents ({len(SAMPLE_INCIDENTS)}):")
        for i in SAMPLE_INCIDENTS[:2]:
            print(f"  {i['incident_id']}: {i['severity']} - {i['root_cause']}")
        print("\nTo seed Convex, set CONVEX_DEPLOYMENT_URL and CONVEX_API_KEY.")
        return

    client = httpx.Client(base_url=CONVEX_URL, headers={"Authorization": f"Bearer {CONVEX_KEY}"})

    print("Seeding deployments...")
    for d in SAMPLE_DEPLOYMENTS:
        try:
            client.post("/api/mutation", json={"path": "deployments:create", "args": d})
            print(f"  {d['deployment_id']}: OK")
        except Exception as e:
            print(f"  {d['deployment_id']}: FAIL ({e})")

    print("Seeding incidents...")
    for i in SAMPLE_INCIDENTS:
        try:
            client.post("/api/mutation", json={"path": "incidents:create", "args": i})
            print(f"  {i['incident_id']}: OK")
        except Exception as e:
            print(f"  {i['incident_id']}: FAIL ({e})")

    print("\nSeeding complete!")

if __name__ == "__main__":
    main()
