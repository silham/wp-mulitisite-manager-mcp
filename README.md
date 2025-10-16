# WordPress Multi-Site MCP Server

A Model Context Protocol (MCP) server for managing multiple WordPress sites simultaneously.

## Features

### Multi-Site Support
- Configure and manage multiple WordPress sites from environment variables
- Each site has independent authentication and configuration
- Easy site switching in tool calls

### Available Tools

1. **get_available_sites()** - List all configured WordPress sites
2. **get_post_by_id(site_name, post_id)** - Fetch a specific post
3. **get_recent_posts(site_name, count)** - Get recent posts from a site
4. **search_posts(site_name, search_term, count)** - Search posts on a site
5. **get_post_categories(site_name)** - Get all categories from a site
6. **get_posts_by_category(site_name, category_id, count)** - Get posts by category

### Available Resources

- **sites://list** - Display formatted list of all configured sites

## Setup

### 1. Configure WordPress Sites

Edit `.env` file to add your WordPress sites:

```bash
# Site 1
SITE_GOOGLERANK_URL=https://googlerank.com.au
SITE_GOOGLERANK_USER=goto@digifix.com.au
SITE_GOOGLERANK_APP_PASSWORD=iUGn XOkL QPvs q6jv CCI1 xWAd

# Site 2
# WordPress Multi-Site MCP Server

A powerful Model Context Protocol (MCP) server that provides Claude AI with comprehensive access to multiple WordPress sites via their REST API. Supports full CRUD operations on posts, pages, categories, tags, users, comments, and more.

## 🌟 Features

- **Multi-Site Support** - Manage multiple WordPress sites from a single MCP server
- **Complete REST API Coverage** - 30+ tools for all major WordPress operations
- **Full CRUD Operations** - Create, Read, Update, Delete for posts, pages, tags, categories, users, comments
- **Secure Authentication** - Token-based authentication for server access
- **Remote Deployment** - HTTP/SSE transport for hosting on remote servers
- **Flexible Credentials** - Store WordPress credentials on server or in Claude config
- **Health Monitoring** - Built-in health checks and status endpoints

## 🚀 Quick Start

### Local Development

1. **Clone and Install**
   ```bash
   git clone https://github.com/silham/learn-mcp.git
   cd mcp-server-demo
   cp .env.example .env
   # Edit .env with your WordPress credentials
   ```

2. **Configure WordPress Sites**
   ```bash
   # Generate auth token
   openssl rand -hex 32
   
   # Add to .env
   MCP_AUTH_TOKEN=your-generated-token
   SITE_MYSITE_URL=https://example.com
   SITE_MYSITE_USER=admin@example.com
   SITE_MYSITE_APP_PASSWORD=xxxx xxxx xxxx xxxx
   ```

3. **Install in Claude**
   ```bash
   uv run mcp install main.py --with requests --with python-dotenv --env-file .env
   ```

### Remote Deployment

See **[QUICKSTART_DEPLOYMENT.md](QUICKSTART_DEPLOYMENT.md)** for deploying to Coolify or any Docker host.

## 📖 Documentation

- **[QUICKSTART_DEPLOYMENT.md](QUICKSTART_DEPLOYMENT.md)** - Deploy to Coolify in 3 steps
- **[AUTHENTICATION.md](AUTHENTICATION.md)** - Security setup and credential management
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Comprehensive deployment guide
- **[.env.example](.env.example)** - Environment variable template
- **[claude_desktop_config.example.json](claude_desktop_config.example.json)** - Claude config template

## 🔐 Security

### Two-Level Authentication

1. **MCP Server Auth** - Controls access to the MCP server
2. **WordPress Auth** - Individual site credentials (Application Passwords)

### Credential Configuration Options

**Option A: Server-Side (Simpler)**
```bash
# .env file
MCP_AUTH_TOKEN=your-token
SITE_MYSITE_URL=https://example.com
SITE_MYSITE_USER=admin@example.com
SITE_MYSITE_APP_PASSWORD=xxxx xxxx
```

**Option B: Client-Side (More Secure - Recommended)**
```json
{
  "mcpServers": {
    "wordpress": {
      "url": "https://mcp.yourdomain.com/sse",
      "headers": {
        "Authorization": "Bearer your-token"
      },
      "env": {
        "SITE_MYSITE_URL": "https://example.com",
        "SITE_MYSITE_USER": "admin@example.com",
        "SITE_MYSITE_APP_PASSWORD": "xxxx xxxx"
      }
    }
  }
}
```

See **[AUTHENTICATION.md](AUTHENTICATION.md)** for complete security guide.

## 🛠️ Available Tools

### Site Management
- `get_available_sites` - List all configured WordPress sites
- `get_site_info` - Get WordPress version and site information

### Posts
- `get_posts` / `get_post` - Retrieve posts with filtering
- `get_posts_summary` - Lightweight post overview
- `create_post` - Create new posts
- `update_post` - Update existing posts
- `delete_post` - Delete posts

### Pages
- `get_pages` / `get_page` - Retrieve pages
- `create_page` - Create new pages
- `update_page` - Update existing pages
- `delete_page` - Delete pages

### Categories & Tags
- `get_categories` / `get_category` - Manage categories
- `create_category` / `update_category` / `delete_category`
- `get_tags` / `get_tag` - Manage tags
- `create_tag` / `update_tag` / `delete_tag`

### Users
- `get_users` / `get_user` / `get_current_user`
- `create_user` / `update_user` / `delete_user`

### Comments
- `get_comments` / `get_comment`
- `create_comment` / `update_comment` / `delete_comment`

### Media
- `get_media` / `get_media_item` - Browse and retrieve media

See full list with `get_available_sites` tool in Claude.

## 📊 Architecture

```
┌─────────────────┐
│   Claude AI     │
│  (MCP Client)   │
└────────┬────────┘
         │ SSE/HTTP or stdio
         │
┌────────▼────────────┐
│  MCP Server (This)  │
│  - Authentication   │
│  - Multi-site mgmt  │
│  - 30+ WP tools     │
└────────┬────────────┘
         │ REST API
         │
┌────────▼────────┐  ┌──────────────┐  ┌──────────────┐
│ WordPress Site 1│  │ WP Site 2    │  │ WP Site N    │
└─────────────────┘  └──────────────┘  └──────────────┘
```

## 🔧 Configuration

### Environment Variables

**Server Authentication:**
```bash
MCP_AUTH_TOKEN=your-secure-token  # Optional but recommended for production
```

**WordPress Sites (repeat for each site):**
```bash
SITE_<NAME>_URL=https://example.com
SITE_<NAME>_USER=username@example.com
SITE_<NAME>_APP_PASSWORD=xxxx xxxx xxxx xxxx
```

**How to get WordPress Application Password:**
1. WordPress Admin → Users → Profile
2. Scroll to "Application Passwords"
3. Create new password with name "MCP Server"
4. Copy generated password

### Claude Desktop Config

**Local (stdio):**
```json
{
  "mcpServers": {
    "wordpress": {
      "command": "uv",
      "args": ["run", "main.py"],
      "cwd": "/path/to/mcp-server-demo",
      "env": {
        "SITE_MYSITE_URL": "https://example.com",
        "SITE_MYSITE_USER": "admin@example.com",
        "SITE_MYSITE_APP_PASSWORD": "xxxx xxxx"
      }
    }
  }
}
```

**Remote (SSE):**
```json
{
  "mcpServers": {
    "wordpress-remote": {
      "url": "https://mcp.yourdomain.com/sse",
      "transport": "sse",
      "headers": {
        "Authorization": "Bearer your-auth-token"
      },
      "env": {
        "SITE_MYSITE_URL": "https://example.com",
        "SITE_MYSITE_USER": "admin@example.com",
        "SITE_MYSITE_APP_PASSWORD": "xxxx xxxx"
      }
    }
  }
}
```

## 🧪 Testing

### Health Check
```bash
curl https://mcp.yourdomain.com/health
```

### SSE Connection (with auth)
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" https://mcp.yourdomain.com/sse
```

### Local Server
```bash
./start.sh
# or
uv run python server_http.py
```

## 🐳 Docker Deployment

```bash
# Build
docker build -t wordpress-mcp .

# Run
docker run -p 8000:8000 --env-file .env wordpress-mcp

# Docker Compose
docker-compose up -d
```

## 📝 Project Structure

```
mcp-server-demo/
├── main.py                     # MCP server core with all tools
├── server_http.py              # HTTP/SSE wrapper for remote access
├── pyproject.toml              # Python dependencies
├── .env                        # Environment config (not in git)
├── .env.example                # Template
├── Dockerfile                  # Container definition
├── docker-compose.yml          # Container orchestration
├── start.sh                    # Local server startup script
├── README.md                   # This file
├── QUICKSTART_DEPLOYMENT.md    # Quick deployment guide
├── AUTHENTICATION.md           # Security documentation
├── DEPLOYMENT.md               # Comprehensive deployment guide
└── claude_desktop_config.example.json  # Claude config template
```

## 🤝 Contributing

Contributions welcome! This is a learning project demonstrating MCP capabilities.

## 📄 License

MIT License - feel free to use and modify.

## 🙏 Acknowledgments

- Built with [Model Context Protocol (MCP)](https://modelcontextprotocol.io)
- Uses [FastMCP](https://github.com/jlowin/fastmcp) framework
- WordPress REST API v2

## 🆘 Support

- Check documentation in AUTHENTICATION.md and DEPLOYMENT.md
- Review example configs
- Test with health endpoints
- Check server logs for errors

## 🔄 Version

**Version:** 1.0.0  
**Last Updated:** October 2025  
**MCP Protocol:** 2024-11-05

# Add as many sites as needed...
```

**Environment Variable Pattern:**
- `SITE_<NAME>_URL` - WordPress site URL
- `SITE_<NAME>_USER` - WordPress username
- `SITE_<NAME>_APP_PASSWORD` - WordPress Application Password

**Site Name Rules:**
- Can be any alphanumeric string with underscores
- Will be converted to lowercase for use in tools
- Example: `SITE_GOOGLERANK` becomes `googlerank`

### 2. Generate WordPress Application Passwords

For each WordPress site:

1. Log into WordPress admin
2. Go to **Users → Your Profile**
3. Scroll to **Application Passwords** section
4. Enter a name (e.g., "MCP Server")
5. Click **Add New Application Password**
6. Copy the generated password (spaces included)
7. Add to your `.env` file

### 3. Install the MCP Server

```bash
cd /Users/shakil/Dev/learn/mcp/mcp-server-demo
uv run mcp install main.py --with requests --with python-dotenv --env-file .env
```

**Important:** Always include:
- `--with requests` - HTTP client
- `--with python-dotenv` - Environment variable loading
- `--env-file .env` - Path to your environment file

### 4. Restart Claude

1. Completely quit Claude (Cmd+Q)
2. Restart Claude
3. The server should appear as "WordPress Multi-Site Manager"

## Usage Examples

### In Claude

Once connected, you can use the MCP tools:

**List all configured sites:**
```
Use the get_available_sites tool
```

**Get recent posts from a specific site:**
```
Get the 5 most recent posts from googlerank
```

**Search for posts:**
```
Search for posts about "SEO" on googlerank site
```

**Get categories:**
```
Show me all categories on the googlerank site
```

### Local Testing

Test the server locally before using in Claude:

```bash
# Test basic functionality
uv run python main.py

# Test specific functions
uv run python -c "
from main import get_available_sites, get_recent_posts
sites = get_available_sites()
print('Sites:', sites)
if sites:
    posts = get_recent_posts(sites[0]['name'], 3)
    print(f'Posts: {len(posts)}')
"
```

## Adding More Sites

1. Edit `.env` file
2. Add new site following the pattern:
   ```bash
   SITE_NEWSITE_URL=https://newsite.com
   SITE_NEWSITE_USER=user@newsite.com
   SITE_NEWSITE_APP_PASSWORD=xxxx xxxx xxxx xxxx
   ```
3. Restart Claude (the .env file is loaded when the server starts)

No need to reinstall the MCP server - just restart Claude to pick up new sites.

## Tool Reference

### get_available_sites()

Returns list of all configured sites with their details.

**Returns:**
```json
[
  {
    "name": "googlerank",
    "url": "https://googlerank.com.au",
    "api_base": "https://googlerank.com.au/wp-json/wp/v2"
  }
]
```

### get_post_by_id(site_name, post_id)

Fetch a specific post by ID.

**Parameters:**
- `site_name` (str): Site name (e.g., "googlerank")
- `post_id` (int): WordPress post ID

**Returns:** Full post object with title, content, metadata, etc.

### get_recent_posts(site_name, count=5)

Get recent published posts.

**Parameters:**
- `site_name` (str): Site name
- `count` (int): Number of posts (default: 5)

**Returns:** List of post objects

### search_posts(site_name, search_term, count=10)

Search for posts matching a term.

**Parameters:**
- `site_name` (str): Site name
- `search_term` (str): Search query
- `count` (int): Max results (default: 10)

**Returns:** List of matching posts

### get_post_categories(site_name)

Get all categories from a site.

**Parameters:**
- `site_name` (str): Site name

**Returns:** List of category objects

### get_posts_by_category(site_name, category_id, count=10)

Get posts from a specific category.

**Parameters:**
- `site_name` (str): Site name
- `category_id` (int): Category ID
- `count` (int): Number of posts (default: 10)

**Returns:** List of posts in the category

## Troubleshooting

### "No WordPress sites configured" error

**Problem:** The server can't find any configured sites.

**Solution:**
1. Check `.env` file exists and has correct format
2. Verify environment variables follow pattern: `SITE_<NAME>_URL`, etc.
3. Reinstall with `--env-file .env` flag
4. Restart Claude

### "Site 'xyz' not found" error

**Problem:** Requested site name doesn't match any configured site.

**Solution:**
1. Use `get_available_sites()` to see available site names
2. Site names are case-insensitive and converted to lowercase
3. Check `.env` for typos in site names

### Authentication errors

**Problem:** 401 Unauthorized or authentication failures.

**Solution:**
1. Verify Application Password is correct in `.env`
2. Check username is correct
3. Ensure Application Passwords are enabled on the WordPress site
4. Try regenerating the Application Password

### Check Claude MCP Logs

```bash
tail -f ~/Library/Logs/Claude/mcp*.log
```

## Architecture

### Site Configuration (`WordPressSite` class)
- Stores site credentials and URL
- Generates authentication headers
- Provides API base URL

### Environment Loading (`load_wordpress_sites`)
- Scans environment variables for site configurations
- Validates required fields (URL, user, password)
- Returns dictionary of configured sites

### API Requests (`make_wp_request`)
- Handles all WordPress REST API calls
- Supports GET and POST methods
- Automatic authentication header injection
- Error handling with meaningful messages

## Security Notes

- Never commit `.env` file to git (add to `.gitignore`)
- Application Passwords are safer than regular passwords
- Each app password can be revoked individually
- Store credentials securely
- Use different Application Passwords for different tools

## Future Enhancements

Potential features to add:
- POST/UPDATE/DELETE operations for posts
- Media upload support
- User management
- Plugin/theme information
- Site health checks
- Bulk operations across multiple sites
- Custom post type support
