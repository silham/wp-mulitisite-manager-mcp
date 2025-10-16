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
   
   Copy your WordPress site configurations from `.env`:
   
   ```
   SITE_GOOGLERANK_URL=https://googlerank.com.au
   SITE_GOOGLERANK_USER=goto@digifix.com.au
   SITE_GOOGLERANK_APP_PASSWORD=iUGn XOkL QPvs q6jv CCI1 xWAd
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

Or with IP address:

```json
{
  "mcpServers": {
    "wordpress-remote": {
      "url": "http://SERVER_IP:8000/sse",
      "transport": "sse"
    }
  }
}
```

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
  "site_names": ["googlerank"]
}
```

### Check SSE Endpoint

```bash
curl https://mcp.yourdomain.com/sse
```

Should establish an SSE connection (keeps open).

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

- [ ] Repository pushed to Git
- [ ] `.env.example` committed (without actual credentials)
- [ ] `.env` added to `.gitignore`
- [ ] Coolify application created
- [ ] Environment variables configured in Coolify
- [ ] Domain configured (optional)
- [ ] SSL enabled (if using domain)
- [ ] Deployment successful
- [ ] Health check returns "healthy"
- [ ] Claude config updated
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
- Check firewall/security groups
- Ensure URL is correct in Claude config
- Try HTTP instead of HTTPS for testing

### "No sites configured" Error
- Check environment variables in Coolify
- Verify variable names follow pattern: `SITE_<NAME>_URL`
- View container logs for errors

## 📖 Full Documentation

See `DEPLOYMENT.md` for comprehensive deployment guide including:
- Security best practices
- Authentication setup
- Monitoring and logging
- Performance optimization
- Scaling strategies

## 🔐 Security Notes

**IMPORTANT**: Never commit `.env` file to git!

Your `.env` contains sensitive credentials. Always:
1. Use `.env.example` for templates
2. Add `.env` to `.gitignore`
3. Configure actual credentials in Coolify UI
4. Enable HTTPS for production
5. Consider adding authentication token

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
