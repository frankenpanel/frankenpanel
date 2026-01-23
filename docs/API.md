# FrankenPanel REST API Documentation

## Base URL

```
https://your-domain.com/api/v1
```

## Authentication

All API endpoints (except `/auth/login`) require authentication via JWT token.

### Login

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "password"
}
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "is_active": true,
    "is_superuser": true
  }
}
```

### Using the Token

Include the token in the Authorization header:

```http
Authorization: Bearer eyJ...
```

Or use the session cookie (set automatically on login).

## Endpoints

### Authentication

- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/logout` - Logout
- `GET /api/v1/auth/me` - Get current user
- `POST /api/v1/auth/refresh` - Refresh token

### Users

- `GET /api/v1/users/` - List users
- `POST /api/v1/users/` - Create user
- `GET /api/v1/users/{id}` - Get user
- `PUT /api/v1/users/{id}` - Update user
- `DELETE /api/v1/users/{id}` - Delete user
- `GET /api/v1/users/roles/` - List roles
- `POST /api/v1/users/roles/` - Create role

### Sites

- `GET /api/v1/sites/` - List sites
- `POST /api/v1/sites/` - Create site
- `GET /api/v1/sites/{id}` - Get site
- `PUT /api/v1/sites/{id}` - Update site
- `DELETE /api/v1/sites/{id}` - Delete site
- `POST /api/v1/sites/{id}/start` - Start site
- `POST /api/v1/sites/{id}/stop` - Stop site

### Databases

- `GET /api/v1/databases/` - List databases
- `POST /api/v1/databases/` - Create database
- `GET /api/v1/databases/{id}` - Get database
- `PUT /api/v1/databases/{id}` - Update database
- `DELETE /api/v1/databases/{id}` - Delete database

### Domains

- `GET /api/v1/domains/` - List domains
- `POST /api/v1/domains/` - Create domain
- `PUT /api/v1/domains/{id}` - Update domain
- `DELETE /api/v1/domains/{id}` - Delete domain

### Backups

- `GET /api/v1/backups/` - List backups
- `POST /api/v1/backups/` - Create backup
- `GET /api/v1/backups/{id}` - Get backup
- `POST /api/v1/backups/restore` - Restore backup
- `DELETE /api/v1/backups/{id}` - Delete backup

### Audit Logs

- `GET /api/v1/audit/` - List audit logs (superuser only)
- `GET /api/v1/audit/{id}` - Get audit log (superuser only)

## Example: Creating a Site

```bash
curl -X POST https://your-domain.com/api/v1/sites/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My WordPress Site",
    "site_type": "wordpress",
    "domain": "example.com",
    "php_version": "8.2",
    "create_database": true
  }'
```

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message"
}
```

Common status codes:
- `200` - Success
- `201` - Created
- `204` - No Content
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error
