# Runbook: Service Restart

## When to Use
- Service health check failing
- OOM killed event
- Crash loop detected
- Connection pool exhausted

## Prerequisites
- SSH access or Docker access to the host
- Knowledge of which service needs restart
- Verify no active deployment in progress

## Procedure

### 1. Verify the Issue
```bash
docker ps | grep <service-name>
docker logs --tail 100 <container-id>
```

### 2. Check for Active Deployments
Verify no deployment is currently running to avoid conflicts.

### 3. Restart the Service
```bash
# Docker Compose
docker compose restart <service-name>

# Or direct Docker
docker restart <container-id>
```

### 4. Verify Recovery
```bash
# Wait 30 seconds for startup
sleep 30

# Check health
curl -sf http://localhost:<port>/health

# Check logs for errors
docker logs --tail 50 <container-id>
```

### 5. Post-Restart
- Verify metrics normalize (error rate, latency)
- Check if restart resolved the underlying issue
- If service crashes again within 5 minutes, escalate to engineering

## Rollback
If restart causes additional issues, stop the service and escalate immediately.

## Auto-Resolution
Ops NEop can auto-restart services for known patterns (max 3 restarts per hour).
