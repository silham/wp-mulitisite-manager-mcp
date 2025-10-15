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
SITE_MYSITE_URL=https://mysite.com
SITE_MYSITE_USER=admin@mysite.com
SITE_MYSITE_APP_PASSWORD=xxxx xxxx xxxx xxxx

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
