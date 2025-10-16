# Authentication & Security Guide

## Overview

The WordPress MCP Server supports two levels of security:

1. **MCP Server Authentication** - Controls who can access the MCP server
2. **WordPress Site Authentication** - Individual site credentials

## MCP Server Authentication

### Enabling Authentication

Set an authentication token in your environment:

```bash
# Generate a secure token (32 bytes = 64 hex characters)
openssl rand -hex 32

# Add to .env file (for local/Docker)
MCP_AUTH_TOKEN=your-generated-token-here
```

### Without Authentication (Development Only)

If `MCP_AUTH_TOKEN` is not set, the server allows unauthenticated access. This is only recommended for:
- Local development
- Servers behind VPN/private networks
- Testing purposes

⚠️ **Never run without authentication on public internet!**

## Configuration Methods

### Method 1: Environment Variables (Server Side)

For Docker/Coolify deployment, set WordPress credentials on the server:

**In `.env` file:**
```bash
# Server authentication
MCP_AUTH_TOKEN=abc123def456...

# WordPress sites
SITE_GOOGLERANK_URL=https://googlerank.com.au
SITE_GOOGLERANK_USER=goto@digifix.com.au
SITE_GOOGLERANK_APP_PASSWORD=xxxx xxxx xxxx xxxx
```

**Claude config (`claude_desktop_config.json`):**
```json
{
  "mcpServers": {
    "wordpress-remote": {
      "url": "https://mcp.yourdomain.com/sse",
      "transport": "sse",
      "headers": {
        "Authorization": "Bearer abc123def456..."
      }
    }
  }
}
```

### Method 2: Environment Variables in Claude Config (Recommended)

Pass WordPress credentials from Claude config:

**Server `.env` (minimal):**
```bash
# Only server authentication token
MCP_AUTH_TOKEN=abc123def456...
```

**Claude config (`claude_desktop_config.json`):**
```json
{
  "mcpServers": {
    "wordpress-remote": {
      "url": "https://mcp.yourdomain.com/sse",
      "transport": "sse",
      "headers": {
        "Authorization": "Bearer abc123def456..."
      },
      "env": {
        "SITE_GOOGLERANK_URL": "https://googlerank.com.au",
        "SITE_GOOGLERANK_USER": "goto@digifix.com.au",
        "SITE_GOOGLERANK_APP_PASSWORD": "xxxx xxxx xxxx xxxx",
        "SITE_BLOG_URL": "https://blog.example.com",
        "SITE_BLOG_USER": "editor@example.com",
        "SITE_BLOG_APP_PASSWORD": "yyyy yyyy yyyy yyyy"
      }
    }
  }
}
```

**Benefits of Method 2:**
- ✅ Credentials stored locally on your machine
- ✅ No credentials on remote server
- ✅ Each user can have their own WordPress accounts
- ✅ Easier to update credentials (just edit local config)
- ✅ Better security - credentials never leave your machine

## Claude Desktop Config Location

**macOS:**
```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```bash
%APPDATA%\Claude\claude_desktop_config.json
```

**Linux:**
```bash
~/.config/Claude/claude_desktop_config.json
```

## Security Best Practices

### 1. Generate Strong Tokens

```bash
# Method 1: OpenSSL (64 character hex)
openssl rand -hex 32

# Method 2: Python
python3 -c "import secrets; print(secrets.token_hex(32))"

# Method 3: Node.js
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

### 2. Never Commit Secrets

Add to `.gitignore`:
```
.env
.env.local
.env.production
claude_desktop_config.json
```

### 3. Use HTTPS in Production

Always use HTTPS for remote MCP servers:
```json
{
  "url": "https://mcp.yourdomain.com/sse"  // ✅ HTTPS
}
```

Not:
```json
{
  "url": "http://mcp.yourdomain.com/sse"  // ❌ HTTP
}
```

### 4. Rotate Tokens Regularly

Update your `MCP_AUTH_TOKEN` periodically:
```bash
# Generate new token
NEW_TOKEN=$(openssl rand -hex 32)

# Update server .env
echo "MCP_AUTH_TOKEN=$NEW_TOKEN" >> .env

# Update Claude config
# Edit claude_desktop_config.json with new token

# Restart server and Claude
```

### 5. WordPress Application Passwords

Use WordPress Application Passwords (not your main password):

1. Go to WordPress Admin → Users → Profile
2. Scroll to "Application Passwords"
3. Create new password with name "MCP Server"
4. Copy the generated password
5. Revoke password if compromised

## Testing Authentication

### Test Server Health (No Auth Required)

```bash
curl https://mcp.yourdomain.com/health
```

Should return:
```json
{
  "status": "healthy",
  "auth_enabled": true,
  "sites_configured": 1
}
```

### Test SSE Endpoint (Auth Required)

```bash
# Without token (should fail)
curl https://mcp.yourdomain.com/sse
# Returns: {"error": "Unauthorized"}

# With token (should connect)
curl -H "Authorization: Bearer YOUR_TOKEN" https://mcp.yourdomain.com/sse
# Keeps connection open
```

### Test from Claude

After configuring, restart Claude and check:
1. Open Claude
2. Look for WordPress tools in the command palette
3. Try `get_available_sites` tool
4. Should return your configured sites

## Troubleshooting

### "Unauthorized" Error

**Symptom:** Claude can't connect, shows 401 error

**Solutions:**
1. Check `MCP_AUTH_TOKEN` is set on server
2. Verify token in Claude config matches server token
3. Ensure `Authorization` header is properly formatted:
   ```json
   "Authorization": "Bearer YOUR_TOKEN"
   ```
4. Restart Claude after config changes

### Sites Not Loading

**Symptom:** Health check shows `sites_configured: 0`

**Solutions:**
1. Check environment variables follow pattern: `SITE_<NAME>_URL`
2. Verify credentials are correct
3. Test WordPress site is accessible
4. Check server logs:
   ```bash
   docker logs -f mcp-wordpress
   ```

### Authentication Bypassed

**Symptom:** Can access without token

**Cause:** `MCP_AUTH_TOKEN` not set on server

**Solution:**
```bash
# Set token in .env
echo "MCP_AUTH_TOKEN=$(openssl rand -hex 32)" >> .env

# Restart server
docker-compose restart
```

## Multi-User Setup

For teams, each user can have their own credentials:

**Server `.env`:**
```bash
MCP_AUTH_TOKEN=server-secret-token
# No WordPress credentials here
```

**User 1 Claude config:**
```json
{
  "env": {
    "SITE_BLOG_USER": "user1@example.com",
    "SITE_BLOG_APP_PASSWORD": "user1-password"
  }
}
```

**User 2 Claude config:**
```json
{
  "env": {
    "SITE_BLOG_USER": "user2@example.com",
    "SITE_BLOG_APP_PASSWORD": "user2-password"
  }
}
```

Everyone shares the MCP server token, but has their own WordPress credentials.

## Example Configurations

### Personal Use (Single User)

**Server `.env`:**
```bash
MCP_AUTH_TOKEN=personal-secret-token
SITE_MYBLOG_URL=https://myblog.com
SITE_MYBLOG_USER=me@example.com
SITE_MYBLOG_APP_PASSWORD=xxxx xxxx
```

**Claude config:**
```json
{
  "mcpServers": {
    "wordpress": {
      "url": "https://mcp.mydomain.com/sse",
      "transport": "sse",
      "headers": {
        "Authorization": "Bearer personal-secret-token"
      }
    }
  }
}
```

### Team Use (Multiple Users)

**Server `.env`:**
```bash
MCP_AUTH_TOKEN=team-shared-token
# No WordPress credentials
```

**Each user's Claude config:**
```json
{
  "mcpServers": {
    "wordpress": {
      "url": "https://mcp.company.com/sse",
      "transport": "sse",
      "headers": {
        "Authorization": "Bearer team-shared-token"
      },
      "env": {
        "SITE_COMPANY_URL": "https://company.com",
        "SITE_COMPANY_USER": "alice@company.com",
        "SITE_COMPANY_APP_PASSWORD": "alice-app-password"
      }
    }
  }
}
```

### Development (No Auth)

**Server `.env`:**
```bash
# No MCP_AUTH_TOKEN = authentication disabled
SITE_TEST_URL=http://localhost:8080
SITE_TEST_USER=admin
SITE_TEST_APP_PASSWORD=test test test
```

**Claude config:**
```json
{
  "mcpServers": {
    "wordpress-dev": {
      "url": "http://localhost:8000/sse",
      "transport": "sse"
    }
  }
}
```

## Migration Guide

### From .env Only → .env + Auth

1. Generate auth token:
   ```bash
   openssl rand -hex 32 > .auth_token.txt
   ```

2. Add to server `.env`:
   ```bash
   echo "MCP_AUTH_TOKEN=$(cat .auth_token.txt)" >> .env
   ```

3. Update Claude config:
   ```json
   {
     "headers": {
       "Authorization": "Bearer YOUR_TOKEN_FROM_FILE"
     }
   }
   ```

4. Restart server and Claude

### From Server Credentials → Client Credentials

1. Copy WordPress credentials from server `.env`
2. Add to Claude config `env` section
3. Remove from server `.env` (keep only `MCP_AUTH_TOKEN`)
4. Restart server and Claude
5. Test functionality

## Security Checklist

Before deploying to production:

- [ ] `MCP_AUTH_TOKEN` is set and strong (32+ bytes)
- [ ] Server uses HTTPS (SSL/TLS enabled)
- [ ] `.env` file is in `.gitignore`
- [ ] No credentials in git repository
- [ ] WordPress uses Application Passwords (not main password)
- [ ] Firewall rules limit access if needed
- [ ] Monitoring/logging enabled
- [ ] Regular token rotation schedule
- [ ] Backup authentication credentials securely
- [ ] Team members have individual WordPress accounts

## Need Help?

- Check server logs: `docker logs -f mcp-wordpress`
- Test endpoints with curl
- Verify environment variables: `docker exec mcp-wordpress env | grep SITE_`
- Review Claude logs for connection errors
