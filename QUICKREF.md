# MCP Server - Quick Reference

## Installation

To install or update the MCP server in Claude:

```bash
cd /Users/shakil/Dev/learn/mcp/mcp-server-demo
uv run mcp install main.py --with requests
```

**Important:** Always include `--with requests` to ensure the `requests` package is available.

## Verification

To verify the installation is correct:

```bash
uv run python verify_install.py
```

## Testing Locally

### Test WordPress functions directly:
```bash
uv run python main.py
```

### Run comprehensive tests:
```bash
uv run python test_mcp_server.py
```

## Troubleshooting

### "Server disconnected" in Claude

**Problem:** Claude shows "Server disconnected" after installing the MCP server.

**Solution:**
1. Check the installation includes `requests`:
   ```bash
   cat ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```
   Look for `"--with", "requests"` in the "Demo" server args.

2. If missing, reinstall:
   ```bash
   uv run mcp install main.py --with requests
   ```

3. Completely quit Claude (Cmd+Q) and restart.

### "ModuleNotFoundError: No module named 'requests'"

This means the MCP server was installed without the `--with requests` flag.

**Fix:**
```bash
uv run mcp install main.py --with requests
```

### Check Claude MCP Logs

Logs are located at:
```
~/Library/Logs/Claude/mcp*.log
```

View recent logs:
```bash
tail -f ~/Library/Logs/Claude/mcp*.log
```

## Available MCP Tools

Once connected in Claude, you'll have access to:

1. **get_post_by_id(post_id: int)**
   - Fetch a specific WordPress post by ID
   - Returns full post data including title, content, metadata

2. **get_recent_posts(count: int = 5)**
   - Fetch recent published posts
   - Default: 5 posts
   - Returns list of post data

## Configuration

WordPress credentials are hardcoded in `main.py`:
- Site: https://googlerank.com.au
- Authentication: Application Password (Basic Auth)

To change credentials, edit the `get_wp_auth_headers()` function in `main.py`.

## Project Structure

```
mcp-server-demo/
├── main.py                 # MCP server with WordPress tools
├── test_mcp_server.py      # Comprehensive test suite
├── verify_install.py       # Installation verification script
├── pyproject.toml          # Project dependencies
└── README.md              # Main documentation
```

## Common Commands

```bash
# Install/update MCP server
uv run mcp install main.py --with requests

# Test locally
uv run python main.py

# Run test suite
uv run python test_mcp_server.py

# Verify installation
uv run python verify_install.py

# Check Claude config
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json

# View Claude logs
tail -f ~/Library/Logs/Claude/mcp*.log
```
