# Security Guide

## Security Architecture

FrankenPanel implements a zero-trust security model with multiple layers of protection.

## Authentication & Authorization

### JWT Tokens
- Access tokens expire after 30 minutes
- Refresh tokens expire after 7 days
- Tokens are signed with HS256 algorithm
- Session cookies are HTTP-only and secure

### Role-Based Access Control (RBAC)
- Fine-grained permissions per resource and action
- Users can have multiple roles
- Permissions are checked on every request
- Superusers bypass all permission checks

## Data Encryption

### Secrets Storage
- Database passwords are encrypted using Fernet (symmetric encryption)
- Encryption key is stored in environment variables
- Never log or expose encrypted secrets

### Backups
- Backups can be encrypted at rest
- Encryption uses the same encryption key
- Backup files are stored with restricted permissions (600)

## Network Security

### Firewall
- Only ports 22 (SSH), 80 (HTTP), and 443 (HTTPS) are open
- All internal services bind to 127.0.0.1
- FrankenPHP workers are not directly accessible

### HTTPS
- Caddy automatically provisions SSL certificates
- HTTPS is enforced for all domains
- HSTS headers are set

## Input Validation

- All API inputs are validated using Pydantic schemas
- SQL injection prevention via SQLAlchemy ORM
- XSS protection via content security headers
- CSRF protection via same-site cookies

## Audit Logging

- All critical operations are logged
- Logs include: user, action, resource, IP address, timestamp
- Logs are immutable and cannot be deleted by non-superusers
- Logs are stored in PostgreSQL for queryability

## Security Headers

The following headers are set on all responses:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- `Content-Security-Policy: default-src 'self'`

## Rate Limiting

- API requests are rate-limited (60/minute, 1000/hour)
- Prevents brute force attacks
- Configurable per endpoint

## Best Practices

1. **Change Default Passwords**: Immediately change all default passwords after installation
2. **Use Strong Passwords**: Minimum 8 characters, mix of letters, numbers, symbols
3. **Regular Updates**: Keep system and dependencies updated
4. **Monitor Logs**: Regularly review audit logs for suspicious activity
5. **Backup Encryption**: Enable backup encryption for sensitive data
6. **Principle of Least Privilege**: Assign minimal required permissions
7. **Regular Backups**: Schedule automated backups
8. **Security Updates**: Monitor and apply security patches promptly

## Security Checklist

- [ ] Changed default PostgreSQL password
- [ ] Changed default MySQL root password
- [ ] Changed SECRET_KEY in .env
- [ ] Changed ENCRYPTION_KEY in .env
- [ ] Configured firewall rules
- [ ] Enabled fail2ban
- [ ] Set up SSL certificates
- [ ] Configured backup encryption
- [ ] Created non-superuser accounts with appropriate roles
- [ ] Reviewed and configured audit logging
- [ ] Set up monitoring and alerting
