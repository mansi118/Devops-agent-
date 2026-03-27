# Runbook: TLS Certificate Renewal

## Auto-Renewal Process
Ops NEop monitors certificate expiry and auto-renews via Let's Encrypt 7 days before expiry.

## Manual Renewal
If auto-renewal fails:

```bash
# Check current certificate
openssl s_client -connect domain.neuraledge.in:443 -servername domain.neuraledge.in 2>/dev/null | openssl x509 -noout -dates

# Renew via certbot
sudo certbot renew --cert-name domain.neuraledge.in

# Restart affected service
sudo systemctl restart nginx
# or
docker compose restart <service>
```

## Verification
```bash
# Verify new certificate
curl -vI https://domain.neuraledge.in 2>&1 | grep "expire date"
```

## Troubleshooting
- **DNS not pointing correctly**: Verify A record points to correct IP
- **Port 80 blocked**: Let's Encrypt needs HTTP validation; ensure port 80 is open
- **Rate limited**: Let's Encrypt has rate limits (5 certs/week/domain); wait or use staging
- **Wildcard cert issues**: Requires DNS-01 challenge; check DNS provider API access
