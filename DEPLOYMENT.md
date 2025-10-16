# Deploying WordPress MCP Server to Coolify

This guide explains how to deploy the WordPress Multi-Site MCP Server to a remote server using Coolify.

## Overview

The MCP server will run as a Docker container on your Coolify-powered server, accessible via HTTP/SSE (Server-Sent Events) transport for remote MCP client connections.

## Prerequisites

1. **Coolify server** - Running and accessible
2. **Docker** - Installed on the server (Coolify handles this)
3. **WordPress sites** - Configured with Application Passwords
4. **Domain/subdomain** (optional) - For accessing the MCP server

## Deployment Steps

### 1. Prepare Your Repository

Ensure your repository contains these files:
- `main.py` - Main MCP server code
- `server_http.py` - HTTP/SSE wrapper
- `Dockerfile` - Container definition
- `docker-compose.yml` - Docker composition
- `pyproject.toml` - Python dependencies
- `.env.example` - Environment template

### 2. Push to Git Repository

```bash
# Initialize git if not already done
git init
git add .
git commit -m "Add MCP server deployment files"

# Push to your git hosting (GitHub, GitLab, etc.)
git remote add origin <your-repo-url>
git push -u origin main
```

### 3. Configure Coolify

#### Option A: Using Coolify UI

1. **Login to Coolify Dashboard**
   - Navigate to your Coolify instance

2. **Create New Application**
   - Click "New Resource" → "Application"
   - Select "Public Repository" or "Private Repository"
   - Enter your repository URL

3. **Configure Build Settings**
   - **Build Pack**: Docker
   - **Dockerfile Location**: `./Dockerfile`
   - **Port**: `8000`

4. **Set Environment Variables**
   Add all your WordPress site configurations:
   ```
   SITE_GOOGLERANK_URL=https://googlerank.com.au
   SITE_GOOGLERANK_USER=goto@digifix.com.au
   SITE_GOOGLERANK_APP_PASSWORD=iUGn XOkL QPvs q6jv CCI1 xWAd
   
   # Add more sites as needed
   SITE_MYSITE_URL=https://mysite.com
   SITE_MYSITE_USER=user@mysite.com
   SITE_MYSITE_APP_PASSWORD=xxxx xxxx xxxx xxxx
   ```

5. **Configure Domain (Optional)**
   - Set up a domain/subdomain: `mcp.yourdomain.com`
   - Enable SSL/HTTPS (recommended)

6. **Deploy**
   - Click "Deploy"
   - Coolify will build and start your container

#### Option B: Using Docker Compose Directly

If your Coolify supports docker-compose deployments:

1. Upload your project files to the server
2. Configure `.env` file with your credentials
3. Run: `docker-compose up -d`

### 4. Verify Deployment

Once deployed, verify the server is running:

```bash
# Check if the server is responding
curl http://your-server-url:8000/sse

# Or if using a domain
curl https://mcp.yourdomain.com/sse
```

You should see an SSE stream connection attempt.

## Connecting Claude to Remote MCP Server

### Update Claude Desktop Configuration

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "wordpress-remote": {
      "url": "https://mcp.yourdomain.com/sse",
      "transport": "sse"
    }
  }
}
```

Or if using IP address and port:

```json
{
  "mcpServers": {
    "wordpress-remote": {
      "url": "http://your-server-ip:8000/sse",
      "transport": "sse"
    }
  }
}
```

### Restart Claude

Completely quit and restart Claude (Cmd+Q on Mac).

## Security Considerations

### 1. Use HTTPS

Always use HTTPS in production. Coolify can auto-configure SSL with Let's Encrypt:
- Set up a domain in Coolify
- Enable "Force HTTPS"

### 2. Authentication (Recommended)

Add basic authentication to your MCP server:

**Update `server_http.py`:**

```python
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
import base64
import os

# Add authentication middleware
def verify_auth(auth_header):
    if not auth_header:
        return False
    
    expected_token = os.getenv("MCP_AUTH_TOKEN", "your-secret-token")
    
    try:
        scheme, credentials = auth_header.split()
        if scheme.lower() == 'bearer':
            return credentials == expected_token
    except:
        pass
    
    return False

# Add to Starlette app configuration
```

**Add to `.env`:**
```
MCP_AUTH_TOKEN=your-very-secret-token-here
```

**Update Claude config:**
```json
{
  "mcpServers": {
    "wordpress-remote": {
      "url": "https://mcp.yourdomain.com/sse",
      "transport": "sse",
      "headers": {
        "Authorization": "Bearer your-very-secret-token-here"
      }
    }
  }
}
```

### 3. Firewall Rules

If not using a reverse proxy, configure firewall to allow only specific IPs:

```bash
# Allow only your IP
ufw allow from YOUR_IP_ADDRESS to any port 8000

# Or use Coolify's built-in network isolation
```

## Environment Variables Reference

Add these to Coolify environment configuration:

```bash
# WordPress Site 1
SITE_SITE1_URL=https://example1.com
SITE_SITE1_USER=admin@example1.com
SITE_SITE1_APP_PASSWORD=xxxx xxxx xxxx xxxx

# WordPress Site 2
SITE_SITE2_URL=https://example2.com
SITE_SITE2_USER=admin@example2.com
SITE_SITE2_APP_PASSWORD=xxxx xxxx xxxx xxxx

# Optional: MCP Server Authentication
MCP_AUTH_TOKEN=your-secret-token

# Optional: Logging Level
LOG_LEVEL=INFO
```

## Monitoring & Logs

### View Logs in Coolify

1. Go to your application in Coolify
2. Click "Logs" tab
3. View real-time container logs

### View Logs via Docker

```bash
# SSH into your server
ssh user@your-server

# View logs
docker logs -f wordpress-mcp-server

# Or with docker-compose
docker-compose logs -f mcp-server
```

## Updating the Server

### Via Coolify

1. Push changes to your git repository
2. In Coolify, click "Redeploy"
3. Coolify will pull latest code and rebuild

### Manual Update

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

## Troubleshooting

### Server not starting

```bash
# Check container status
docker ps -a

# Check logs
docker logs wordpress-mcp-server

# Check if port is in use
netstat -tulpn | grep 8000
```

### Connection refused

1. Verify container is running: `docker ps`
2. Check firewall rules: `ufw status`
3. Verify environment variables are set
4. Check Coolify port mapping

### Authentication errors

1. Verify WordPress Application Passwords are correct
2. Test WordPress API directly:
   ```bash
   curl -u "user:app_password" https://yoursite.com/wp-json/wp/v2/posts
   ```

### Environment variables not loading

1. Check `.env` file exists in container:
   ```bash
   docker exec wordpress-mcp-server cat .env
   ```
2. Verify Coolify environment configuration
3. Rebuild container after changes

## Performance Optimization

### 1. Enable Container Resource Limits

In Coolify, set resource limits:
- **Memory**: 512MB - 1GB
- **CPU**: 0.5 - 1 core

### 2. Enable Container Restart Policies

Ensure auto-restart on failure:
```yaml
restart: unless-stopped
```

### 3. Use Health Checks

Add to `docker-compose.yml`:
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/sse"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

## Scaling Considerations

For multiple instances or high availability:

1. **Use Load Balancer** - Coolify supports load balancing
2. **Database for State** - If needed for session persistence
3. **Redis for Caching** - Cache WordPress API responses
4. **Multiple Coolify Servers** - Deploy across regions

## Cost Estimation

Typical resource requirements:
- **RAM**: 256MB - 512MB
- **CPU**: Minimal (< 0.5 core)
- **Storage**: < 100MB
- **Bandwidth**: Depends on usage

## Support

For issues:
1. Check Coolify documentation: https://coolify.io/docs
2. Review MCP documentation: https://modelcontextprotocol.io
3. Check container logs for errors
4. Verify WordPress API accessibility

## Next Steps

After successful deployment:
1. Test all MCP tools in Claude
2. Monitor resource usage
3. Set up backup strategies for .env file
4. Configure monitoring alerts in Coolify
5. Document your custom WordPress sites configuration
