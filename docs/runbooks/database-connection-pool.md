# Runbook: Database Connection Pool Issues

## Symptoms
- "Connection pool exhausted" errors in logs
- Increasing response times
- Database connection timeouts
- Growing number of idle connections

## Diagnosis
```bash
# Check active connections
psql -c "SELECT count(*) FROM pg_stat_activity WHERE state = 'active';"
psql -c "SELECT count(*) FROM pg_stat_activity WHERE state = 'idle';"

# Check connection limits
psql -c "SHOW max_connections;"
```

## Quick Fix
1. Restart the affected service (resets connection pool)
2. Monitor connection count returns to normal

## Root Cause Analysis
- Connection leak in application code (connections not returned to pool)
- Pool size too small for current load
- Long-running queries holding connections
- Database slow response causing pool starvation

## Permanent Fix
- Review and fix connection leak in application code
- Adjust pool size: `max_pool_size = max_connections * 0.8 / num_services`
- Add connection timeout: `connection_timeout = 30s`
- Add idle connection reaping: `idle_timeout = 300s`
- Add query timeout: `statement_timeout = 30s`
