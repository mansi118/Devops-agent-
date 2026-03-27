# Runbook: Disk Space Cleanup

## Thresholds
- Warning: < 20% free
- Critical: < 10% free
- Emergency: < 5% free

## Safe Cleanup Targets

### 1. Docker (usually the biggest offender)
```bash
# Remove unused images, containers, volumes
docker system prune -a --volumes -f

# Check space recovered
docker system df
```

### 2. Log Files
```bash
# Truncate large log files (don't delete, may be held by process)
find /var/log -name "*.log" -size +100M -exec truncate -s 0 {} \;

# Rotate logs
logrotate -f /etc/logrotate.conf
```

### 3. Package Cache
```bash
apt-get clean
apt-get autoremove -y
```

### 4. Old Build Artifacts
```bash
# Remove old build cache
rm -rf /tmp/build-cache-*
```

## Verification
```bash
df -h /
# Should show > 20% free
```

## Prevention
- Docker image pruning cron (daily, untagged > 7 days)
- Log rotation configured for all services
- S3 lifecycle policies for build artifacts
