# Remote Deployment Quick Start

## 🚀 Deploy to Coolify in 3 Steps

### Step 1: Prepare Repository

```bash
# Make sure you're in the project directory
cd /Users/shakil/Dev/learn/mcp/mcp-server-demo

# Add deployment files to git
git add Dockerfile docker-compose.yml server_http.py .dockerignore .gitignore
git add DEPLOYMENT.md start.sh

# Commit
git commit -m "Add Coolify deployment configuration"

# Push to your repository
git push origin main
```

### Step 2: Configure Coolify

1. **Login to Coolify** → https://your-coolify-instance.com

2. **Create New Application**
   - Click "+ New Resource"
   - Select "Application"
   - Choose "Public Repository" or "Private Repository"
   - Enter repository URL: `https://github.com/silham/learn-mcp`

3. **Configure Build**
   - Build Pack: **Docker**
   - Dockerfile Location: `./Dockerfile`
   - Port: **8000**

4. **Set Environment Variables**
   
   **Option A: WordPress credentials on server (simpler)**
   
   Copy your WordPress site configurations from `.env`:
   
   ```
   MCP_AUTH_TOKEN=your-generated-token-here
   SITE_GOOGLERANK_URL=https://googlerank.com.au
   SITE_GOOGLERANK_USER=goto@digifix.com.au
   SITE_GOOGLERANK_APP_PASSWORD=iUGn XOkL QPvs q6jv CCI1 xWAd
   ```
   
   **Option B: WordPress credentials in Claude config (more secure)**
   
   Only set authentication token on server:
   ```
   MCP_AUTH_TOKEN=your-generated-token-here
   ```
   
   WordPress credentials will be in Claude config (see Step 3).
   
   💡 **Generate strong auth token:**
   ```bash
   openssl rand -hex 32
   ```
   
   Add more sites as needed using the pattern:
   ```
   SITE_<NAME>_URL=...
   SITE_<NAME>_USER=...
   SITE_<NAME>_APP_PASSWORD=...
   ```

5. **Configure Domain** (Optional but Recommended)
   - Add domain: `mcp.yourdomain.com`
   - Enable SSL (Let's Encrypt)
   - Force HTTPS

6. **Deploy**
   - Click "Deploy" button
   - Wait for build to complete (~2-3 minutes)

### Step 3: Connect Claude

Edit Claude config: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Option A: WordPress credentials on server**

```json
{
  "mcpServers": {
    "wordpress-remote": {
      "url": "https://mcp.yourdomain.com/sse",
      "transport": "sse",
      "headers": {
        "Authorization": "Bearer your-generated-token-here"
      }
    }
  }
}
```

**Option B: WordPress credentials in Claude (Recommended - More Secure)**

```json
{
  "mcpServers": {
    "wordpress-remote": {
      "url": "https://mcp.yourdomain.com/sse",
      "transport": "sse",
      "headers": {
        "Authorization": "Bearer your-generated-token-here"
      },
      "env": {
        "SITE_GOOGLERANK_URL": "https://googlerank.com.au",
        "SITE_GOOGLERANK_USER": "goto@digifix.com.au",
        "SITE_GOOGLERANK_APP_PASSWORD": "iUGn XOkL QPvs q6jv CCI1 xWAd"
      }
    }
  }
}
```

Or with IP address:

```json
{
  "mcpServers": {
    "wordpress-remote": {
      "url": "http://SERVER_IP:8000/sse",
      "transport": "sse",
      "headers": {
        "Authorization": "Bearer your-generated-token-here"
      },
      "env": {
        "SITE_GOOGLERANK_URL": "https://googlerank.com.au",
        "SITE_GOOGLERANK_USER": "goto@digifix.com.au",
        "SITE_GOOGLERANK_APP_PASSWORD": "iUGn XOkL QPvs q6jv CCI1 xWAd"
      }
    }
  }
}
```

**Why Option B is better:**
- ✅ Credentials stay on your machine
- ✅ No credentials on remote server
- ✅ Each team member can use their own WordPress account
- ✅ Easier to update credentials locally

**Restart Claude** (Cmd+Q and reopen)

## ✅ Verify Deployment

### Check Server Health

```bash
# If using domain
curl https://mcp.yourdomain.com/health

# If using IP
curl http://SERVER_IP:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "server": "WordPress Multi-Site Manager",
  "sites_configured": 1,
  "site_names": ["googlerank"],
  "auth_enabled": true
}
```

### Check SSE Endpoint

```bash
# Without auth token (should fail)
curl https://mcp.yourdomain.com/sse

# With auth token (should connect)
curl -H "Authorization: Bearer your-token" https://mcp.yourdomain.com/sse
```

Should establish an SSE connection (keeps open) with valid token.

## 🔧 Local Testing Before Deployment

Test the HTTP server locally:

```bash
# Option 1: Using start script
./start.sh

# Option 2: Manual
uv run python server_http.py

# Option 3: Using Docker
docker-compose up
```

Access locally at: http://localhost:8000

## 📋 Deployment Checklist

- [ ] Generate strong authentication token (`openssl rand -hex 32`)
- [ ] Choose credentials strategy (server vs client)
- [ ] Repository pushed to Git
- [ ] `.env.example` committed (without actual credentials)
- [ ] `.env` added to `.gitignore`
- [ ] Coolify application created
- [ ] Environment variables configured in Coolify (including `MCP_AUTH_TOKEN`)
- [ ] Domain configured (optional)
- [ ] SSL enabled (if using domain)
- [ ] Deployment successful
- [ ] Health check returns "healthy" with `auth_enabled: true`
- [ ] Claude config updated with auth token
- [ ] Claude config updated with WordPress credentials (if using Option B)
- [ ] Claude restarted
- [ ] MCP tools working in Claude

## 🛠️ Troubleshooting

### Build Failed
- Check Dockerfile syntax
- Verify all files committed to git
- Check Coolify build logs

### Container Doesn't Start
- Check environment variables are set
- View container logs in Coolify
- Verify port 8000 is not in use

### Can't Connect from Claude
- Verify SSE endpoint is accessible
- Check authentication token matches in both places
- Ensure `Authorization` header format is correct: `Bearer TOKEN`
- Check firewall/security groups
- Ensure URL is correct in Claude config
- Try HTTP instead of HTTPS for testing

### "No sites configured" Error
- Check environment variables in Coolify
- Verify variable names follow pattern: `SITE_<NAME>_URL`
- View container logs for errors

## 📖 Full Documentation

See these guides for more details:
- `AUTHENTICATION.md` - **Security setup, credential management, multi-user setup**
- `DEPLOYMENT.md` - Comprehensive deployment guide with monitoring and optimization
- `.env.example` - Environment variable template

Key topics in AUTHENTICATION.md:
- Two credential configuration methods
- Security best practices
- Token generation and rotation
- Multi-user team setup
- Troubleshooting authentication issues

## 🔐 Security Notes

**CRITICAL SECURITY FEATURES:**

1. **MCP Server Authentication** - Required for production!
   ```bash
   # Generate strong token
   openssl rand -hex 32
   
   # Set in Coolify
   MCP_AUTH_TOKEN=your-generated-token
   ```

2. **WordPress Credentials** - Two secure options:
   - **Option A**: Store on server (simpler, single user)
   - **Option B**: Store in Claude config (better, multi-user)

3. **HTTPS** - Always use HTTPS in production
   - Encrypts all traffic including credentials
   - Free with Let's Encrypt in Coolify

**IMPORTANT**: Never commit these to git:
- `.env` (contains actual credentials)
- `claude_desktop_config.json` (contains your credentials)

✅ Safe to commit:
- `.env.example` (template only)
- All code files

## 🔄 Updating After Deployment

Push changes and redeploy:

```bash
git add .
git commit -m "Update MCP server"
git push origin main

# In Coolify, click "Redeploy" button
```

## 📊 Monitoring

View logs in Coolify:
1. Go to your application
2. Click "Logs" tab  
3. See real-time output

Or via SSH:
```bash
ssh user@your-server
docker logs -f <container-name>
```

## 💡 Tips

1. **Test locally first** - Run `./start.sh` before deploying
2. **Use domains** - Easier than remembering IPs
3. **Enable SSL** - Always use HTTPS in production
4. **Monitor resources** - Check CPU/memory usage in Coolify
5. **Backup .env** - Keep secure backup of credentials

## 🆘 Support

- Coolify Docs: https://coolify.io/docs
- MCP Docs: https://modelcontextprotocol.io
- This project: https://github.com/silham/learn-mcp
