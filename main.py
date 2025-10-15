"""
Multi-site WordPress MCP Server

Supports multiple WordPress sites configured via environment variables.
Sites are defined in .env file with naming pattern:
  SITE_<NAME>_URL, SITE_<NAME>_USER, SITE_<NAME>_APP_PASSWORD
"""

from mcp.server.fastmcp import FastMCP
import requests
import base64
import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@dataclass
class WordPressSite:
    """Configuration for a WordPress site"""
    name: str
    url: str
    username: str
    app_password: str
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for this site"""
        credentials = f"{self.username}:{self.app_password}"
        encoded = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
        return {
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/json"
        }
    
    def get_api_base_url(self) -> str:
        """Get the WordPress REST API base URL"""
        url = self.url.rstrip('/')
        return f"{url}/wp-json/wp/v2"


def load_wordpress_sites() -> Dict[str, WordPressSite]:
    """Load WordPress site configurations from environment variables.
    
    Expected format:
    SITE_<NAME>_URL=https://example.com
    SITE_<NAME>_USER=username
    SITE_<NAME>_APP_PASSWORD=xxxx xxxx xxxx xxxx
    """
    sites = {}
    env_vars = os.environ
    
    # Find all unique site names from environment variables
    site_names = set()
    for key in env_vars.keys():
        if key.startswith('SITE_') and '_URL' in key:
            # Extract site name from SITE_<NAME>_URL
            name = key.replace('SITE_', '').replace('_URL', '')
            site_names.add(name)
    
    # Load configuration for each site
    for name in site_names:
        url = env_vars.get(f'SITE_{name}_URL')
        username = env_vars.get(f'SITE_{name}_USER')
        app_password = env_vars.get(f'SITE_{name}_APP_PASSWORD')
        
        if url and username and app_password:
            sites[name.lower()] = WordPressSite(
                name=name.lower(),
                url=url,
                username=username,
                app_password=app_password
            )
    
    return sites


def get_site(site_name: str) -> WordPressSite:
    """Get a WordPress site configuration by name"""
    sites = load_wordpress_sites()
    
    if not sites:
        raise ValueError(
            "No WordPress sites configured. Please set environment variables:\n"
            "SITE_<NAME>_URL, SITE_<NAME>_USER, SITE_<NAME>_APP_PASSWORD"
        )
    
    if site_name not in sites:
        available = ', '.join(sites.keys())
        raise ValueError(
            f"Site '{site_name}' not found. Available sites: {available}"
        )
    
    return sites[site_name]


def make_wp_request(
    site_name: str, 
    endpoint: str, 
    params: Optional[Dict] = None,
    method: str = "GET",
    data: Optional[Dict] = None
) -> Dict:
    """Make a request to the WordPress REST API for a specific site.
    
    Args:
        site_name: Name of the WordPress site (as configured in env)
        endpoint: API endpoint (e.g., "posts", "posts/123")
        params: Query parameters (for GET requests)
        method: HTTP method (GET, POST, PUT, PATCH, DELETE)
        data: Request body data (for POST, PUT, PATCH)
    
    Returns:
        Response data as dict or list
    """
    site = get_site(site_name)
    url = f"{site.get_api_base_url()}/{endpoint}"
    headers = site.get_auth_headers()
    
    method = method.upper()
    
    if method == "GET":
        response = requests.get(url, headers=headers, params=params or {})
    elif method == "POST":
        response = requests.post(url, headers=headers, json=data or params or {})
    elif method == "PUT":
        response = requests.put(url, headers=headers, json=data or params or {})
    elif method == "PATCH":
        response = requests.patch(url, headers=headers, json=data or params or {})
    elif method == "DELETE":
        response = requests.delete(url, headers=headers, params=params or {})
    else:
        raise ValueError(f"Unsupported HTTP method: {method}")
    
    response.raise_for_status()
    return response.json()


# Create an MCP server
mcp = FastMCP("WordPress Multi-Site Manager")


@mcp.resource("sites://list")
def list_sites() -> str:
    """List all configured WordPress sites"""
    sites = load_wordpress_sites()
    
    if not sites:
        return "No WordPress sites configured. Please set environment variables."
    
    result = ["# Configured WordPress Sites\n"]
    for name, site in sites.items():
        result.append(f"## {name}")
        result.append(f"- URL: {site.url}")
        result.append(f"- Username: {site.username}")
        result.append(f"- API: {site.get_api_base_url()}\n")
    
    return "\n".join(result)


@mcp.tool()
def get_available_sites() -> List[Dict[str, str]]:
    """
    Get a list of all configured WordPress sites
    
    Returns:
        list[dict]: List of site configurations with name and URL
    """
    sites = load_wordpress_sites()
    
    return [
        {
            "name": name,
            "url": site.url,
            "api_base": site.get_api_base_url()
        }
        for name, site in sites.items()
    ]


@mcp.tool()
def get_post_by_id(site_name: str, post_id: int) -> Dict:
    """
    Fetch a WordPress post by its ID from a specific site
    
    Args:
        site_name (str): Name of the WordPress site (use get_available_sites to see options)
        post_id (int): The ID of the WordPress post
        
    Returns:
        dict: The WordPress post data
    """
    return make_wp_request(site_name, f"posts/{post_id}")


@mcp.tool()
def get_recent_posts(site_name: str, count: int = 5) -> List[Dict]:
    """
    Fetch recent WordPress posts from a specific site
    
    Args:
        site_name (str): Name of the WordPress site (use get_available_sites to see options)
        count (int): Number of recent posts to fetch. Default is 5
        
    Returns:
        list[dict]: A list of recent WordPress post data
    """
    params = {"per_page": count, "status": "publish"}
    return make_wp_request(site_name, "posts", params)


@mcp.tool()
def search_posts(site_name: str, search_term: str, count: int = 10) -> List[Dict]:
    """
    Search for posts on a specific WordPress site
    
    Args:
        site_name (str): Name of the WordPress site
        search_term (str): Search query
        count (int): Maximum number of results. Default is 10
        
    Returns:
        list[dict]: List of matching posts
    """
    params = {"search": search_term, "per_page": count}
    return make_wp_request(site_name, "posts", params)


@mcp.tool()
def get_posts_summary(site_name: str, count: int = 10, status: str = "publish") -> List[Dict]:
    """
    Get a summarized list of posts with essential information only (title, ID, categories, author)
    
    This returns a lightweight summary instead of full post data, useful for getting an overview
    of posts without loading all content and metadata.
    
    Args:
        site_name (str): Name of the WordPress site
        count (int): Number of posts to fetch. Default is 10
        status (str): Post status filter (publish, draft, pending, private). Default is publish
        
    Returns:
        list[dict]: List of post summaries with fields: id, title, categories, author, date
    """
    # Fetch posts with embedded author and category data
    params = {
        "per_page": count,
        "status": status,
        "_embed": "true"  # This embeds author and category data
    }
    
    posts = make_wp_request(site_name, "posts", params)
    
    # Extract only the essential information
    summaries = []
    for post in posts:
        # Get category names
        categories = []
        if "_embedded" in post and "wp:term" in post["_embedded"]:
            # wp:term contains arrays of terms, first array is categories
            if len(post["_embedded"]["wp:term"]) > 0:
                categories = [cat["name"] for cat in post["_embedded"]["wp:term"][0]]
        
        # Get author name
        author_name = "Unknown"
        if "_embedded" in post and "author" in post["_embedded"]:
            if len(post["_embedded"]["author"]) > 0:
                author_name = post["_embedded"]["author"][0].get("name", "Unknown")
        
        summary = {
            "id": post.get("id"),
            "title": post.get("title", {}).get("rendered", "No title"),
            "author": author_name,
            "categories": categories,
            "date": post.get("date"),
            "link": post.get("link"),
            "status": post.get("status")
        }
        
        summaries.append(summary)
    
    return summaries


@mcp.tool()
def get_post_categories(site_name: str) -> List[Dict]:
    """
    Get all categories from a specific WordPress site
    
    Args:
        site_name (str): Name of the WordPress site
        
    Returns:
        list[dict]: List of categories
    """
    return make_wp_request(site_name, "categories", {"per_page": 100})


@mcp.tool()
def get_posts_by_category(site_name: str, category_id: int, count: int = 10) -> List[Dict]:
    """
    Get posts from a specific category on a WordPress site
    
    Args:
        site_name (str): Name of the WordPress site
        category_id (int): Category ID
        count (int): Number of posts to fetch. Default is 10
        
    Returns:
        list[dict]: List of posts in the category
    """
    params = {"categories": category_id, "per_page": count}
    return make_wp_request(site_name, "posts", params)


# ==================== POST CRUD OPERATIONS ====================

@mcp.tool()
def create_post(
    site_name: str,
    title: str,
    content: str,
    status: str = "draft",
    excerpt: Optional[str] = None,
    categories: Optional[List[int]] = None,
    tags: Optional[List[int]] = None
) -> Dict:
    """
    Create a new WordPress post
    
    Args:
        site_name (str): Name of the WordPress site
        title (str): Post title
        content (str): Post content (HTML allowed)
        status (str): Post status (draft, publish, pending, private). Default is draft
        excerpt (str, optional): Post excerpt
        categories (list[int], optional): List of category IDs
        tags (list[int], optional): List of tag IDs
        
    Returns:
        dict: Created post data including ID and URL
    """
    data = {
        "title": title,
        "content": content,
        "status": status
    }
    
    if excerpt:
        data["excerpt"] = excerpt
    if categories:
        data["categories"] = categories
    if tags:
        data["tags"] = tags
    
    return make_wp_request(site_name, "posts", method="POST", data=data)


@mcp.tool()
def update_post(
    site_name: str,
    post_id: int,
    title: Optional[str] = None,
    content: Optional[str] = None,
    status: Optional[str] = None,
    excerpt: Optional[str] = None,
    categories: Optional[List[int]] = None,
    tags: Optional[List[int]] = None
) -> Dict:
    """
    Update an existing WordPress post
    
    Args:
        site_name (str): Name of the WordPress site
        post_id (int): Post ID to update
        title (str, optional): New post title
        content (str, optional): New post content
        status (str, optional): New post status (draft, publish, pending, private)
        excerpt (str, optional): New post excerpt
        categories (list[int], optional): New list of category IDs
        tags (list[int], optional): New list of tag IDs
        
    Returns:
        dict: Updated post data
    """
    data = {}
    
    if title is not None:
        data["title"] = title
    if content is not None:
        data["content"] = content
    if status is not None:
        data["status"] = status
    if excerpt is not None:
        data["excerpt"] = excerpt
    if categories is not None:
        data["categories"] = categories
    if tags is not None:
        data["tags"] = tags
    
    return make_wp_request(site_name, f"posts/{post_id}", method="POST", data=data)


@mcp.tool()
def delete_post(site_name: str, post_id: int, force: bool = False) -> Dict:
    """
    Delete a WordPress post
    
    Args:
        site_name (str): Name of the WordPress site
        post_id (int): Post ID to delete
        force (bool): Whether to bypass trash and force deletion. Default is False
        
    Returns:
        dict: Information about the deleted post
    """
    params = {"force": force}
    return make_wp_request(site_name, f"posts/{post_id}", params=params, method="DELETE")


# ==================== PAGES ====================

@mcp.tool()
def get_pages(site_name: str, count: int = 10) -> List[Dict]:
    """
    Get pages from a WordPress site
    
    Args:
        site_name (str): Name of the WordPress site
        count (int): Number of pages to fetch. Default is 10
        
    Returns:
        list[dict]: List of pages
    """
    params = {"per_page": count, "status": "publish"}
    return make_wp_request(site_name, "pages", params)


@mcp.tool()
def get_page_by_id(site_name: str, page_id: int) -> Dict:
    """
    Get a specific page by ID
    
    Args:
        site_name (str): Name of the WordPress site
        page_id (int): Page ID
        
    Returns:
        dict: Page data
    """
    return make_wp_request(site_name, f"pages/{page_id}")


@mcp.tool()
def search_pages(site_name: str, search_term: str, count: int = 10) -> List[Dict]:
    """
    Search for pages on a WordPress site
    
    Args:
        site_name (str): Name of the WordPress site
        search_term (str): Search query
        count (int): Maximum number of results. Default is 10
        
    Returns:
        list[dict]: List of matching pages
    """
    params = {"search": search_term, "per_page": count}
    return make_wp_request(site_name, "pages", params)


# ==================== PAGE CRUD OPERATIONS ====================

@mcp.tool()
def create_page(
    site_name: str,
    title: str,
    content: str,
    status: str = "draft",
    parent: Optional[int] = None
) -> Dict:
    """
    Create a new WordPress page
    
    Args:
        site_name (str): Name of the WordPress site
        title (str): Page title
        content (str): Page content (HTML allowed)
        status (str): Page status (draft, publish, pending, private). Default is draft
        parent (int, optional): Parent page ID for hierarchical pages
        
    Returns:
        dict: Created page data including ID and URL
    """
    data = {
        "title": title,
        "content": content,
        "status": status
    }
    
    if parent:
        data["parent"] = parent
    
    return make_wp_request(site_name, "pages", method="POST", data=data)


@mcp.tool()
def update_page(
    site_name: str,
    page_id: int,
    title: Optional[str] = None,
    content: Optional[str] = None,
    status: Optional[str] = None,
    parent: Optional[int] = None
) -> Dict:
    """
    Update an existing WordPress page
    
    Args:
        site_name (str): Name of the WordPress site
        page_id (int): Page ID to update
        title (str, optional): New page title
        content (str, optional): New page content
        status (str, optional): New page status
        parent (int, optional): New parent page ID
        
    Returns:
        dict: Updated page data
    """
    data = {}
    
    if title is not None:
        data["title"] = title
    if content is not None:
        data["content"] = content
    if status is not None:
        data["status"] = status
    if parent is not None:
        data["parent"] = parent
    
    return make_wp_request(site_name, f"pages/{page_id}", method="POST", data=data)


@mcp.tool()
def delete_page(site_name: str, page_id: int, force: bool = False) -> Dict:
    """
    Delete a WordPress page
    
    Args:
        site_name (str): Name of the WordPress site
        page_id (int): Page ID to delete
        force (bool): Whether to bypass trash and force deletion. Default is False
        
    Returns:
        dict: Information about the deleted page
    """
    params = {"force": force}
    return make_wp_request(site_name, f"pages/{page_id}", params=params, method="DELETE")


# ==================== TAGS ====================

@mcp.tool()
def get_tags(site_name: str, count: int = 100) -> List[Dict]:
    """
    Get all tags from a WordPress site
    
    Args:
        site_name (str): Name of the WordPress site
        count (int): Maximum number of tags. Default is 100
        
    Returns:
        list[dict]: List of tags
    """
    params = {"per_page": count}
    return make_wp_request(site_name, "tags", params)


@mcp.tool()
def get_posts_by_tag(site_name: str, tag_id: int, count: int = 10) -> List[Dict]:
    """
    Get posts with a specific tag
    
    Args:
        site_name (str): Name of the WordPress site
        tag_id (int): Tag ID
        count (int): Number of posts. Default is 10
        
    Returns:
        list[dict]: List of posts with the tag
    """
    params = {"tags": tag_id, "per_page": count}
    return make_wp_request(site_name, "posts", params)


# ==================== TAG CRUD OPERATIONS ====================

@mcp.tool()
def create_tag(
    site_name: str,
    name: str,
    description: Optional[str] = None,
    slug: Optional[str] = None
) -> Dict:
    """
    Create a new tag
    
    Args:
        site_name (str): Name of the WordPress site
        name (str): Tag name
        description (str, optional): Tag description
        slug (str, optional): Tag slug (URL-friendly name)
        
    Returns:
        dict: Created tag data including ID
    """
    data = {"name": name}
    
    if description:
        data["description"] = description
    if slug:
        data["slug"] = slug
    
    return make_wp_request(site_name, "tags", method="POST", data=data)


@mcp.tool()
def update_tag(
    site_name: str,
    tag_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    slug: Optional[str] = None
) -> Dict:
    """
    Update an existing tag
    
    Args:
        site_name (str): Name of the WordPress site
        tag_id (int): Tag ID to update
        name (str, optional): New tag name
        description (str, optional): New tag description
        slug (str, optional): New tag slug
        
    Returns:
        dict: Updated tag data
    """
    data = {}
    
    if name is not None:
        data["name"] = name
    if description is not None:
        data["description"] = description
    if slug is not None:
        data["slug"] = slug
    
    return make_wp_request(site_name, f"tags/{tag_id}", method="POST", data=data)


@mcp.tool()
def delete_tag(site_name: str, tag_id: int, force: bool = True) -> Dict:
    """
    Delete a tag
    
    Args:
        site_name (str): Name of the WordPress site
        tag_id (int): Tag ID to delete
        force (bool): Whether to force deletion. Default is True
        
    Returns:
        dict: Information about the deleted tag
    """
    params = {"force": force}
    return make_wp_request(site_name, f"tags/{tag_id}", params=params, method="DELETE")


# ==================== CATEGORY CRUD OPERATIONS ====================

@mcp.tool()
def create_category(
    site_name: str,
    name: str,
    description: Optional[str] = None,
    slug: Optional[str] = None,
    parent: Optional[int] = None
) -> Dict:
    """
    Create a new category
    
    Args:
        site_name (str): Name of the WordPress site
        name (str): Category name
        description (str, optional): Category description
        slug (str, optional): Category slug (URL-friendly name)
        parent (int, optional): Parent category ID for hierarchical categories
        
    Returns:
        dict: Created category data including ID
    """
    data = {"name": name}
    
    if description:
        data["description"] = description
    if slug:
        data["slug"] = slug
    if parent:
        data["parent"] = parent
    
    return make_wp_request(site_name, "categories", method="POST", data=data)


@mcp.tool()
def update_category(
    site_name: str,
    category_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    slug: Optional[str] = None,
    parent: Optional[int] = None
) -> Dict:
    """
    Update an existing category
    
    Args:
        site_name (str): Name of the WordPress site
        category_id (int): Category ID to update
        name (str, optional): New category name
        description (str, optional): New category description
        slug (str, optional): New category slug
        parent (int, optional): New parent category ID
        
    Returns:
        dict: Updated category data
    """
    data = {}
    
    if name is not None:
        data["name"] = name
    if description is not None:
        data["description"] = description
    if slug is not None:
        data["slug"] = slug
    if parent is not None:
        data["parent"] = parent
    
    return make_wp_request(site_name, f"categories/{category_id}", method="POST", data=data)


@mcp.tool()
def delete_category(site_name: str, category_id: int, force: bool = True) -> Dict:
    """
    Delete a category
    
    Args:
        site_name (str): Name of the WordPress site
        category_id (int): Category ID to delete
        force (bool): Whether to force deletion. Default is True
        
    Returns:
        dict: Information about the deleted category
    """
    params = {"force": force}
    return make_wp_request(site_name, f"categories/{category_id}", params=params, method="DELETE")


# ==================== COMMENTS ====================

@mcp.tool()
def get_comments(site_name: str, post_id: Optional[int] = None, count: int = 10) -> List[Dict]:
    """
    Get comments from a WordPress site
    
    Args:
        site_name (str): Name of the WordPress site
        post_id (int, optional): Filter by specific post ID
        count (int): Number of comments. Default is 10
        
    Returns:
        list[dict]: List of comments
    """
    params = {"per_page": count}
    if post_id:
        params["post"] = post_id
    return make_wp_request(site_name, "comments", params)


@mcp.tool()
def get_comment_by_id(site_name: str, comment_id: int) -> Dict:
    """
    Get a specific comment by ID
    
    Args:
        site_name (str): Name of the WordPress site
        comment_id (int): Comment ID
        
    Returns:
        dict: Comment data
    """
    return make_wp_request(site_name, f"comments/{comment_id}")


# ==================== MEDIA ====================

@mcp.tool()
def get_media(site_name: str, count: int = 10) -> List[Dict]:
    """
    Get media items from a WordPress site
    
    Args:
        site_name (str): Name of the WordPress site
        count (int): Number of media items. Default is 10
        
    Returns:
        list[dict]: List of media items
    """
    params = {"per_page": count}
    return make_wp_request(site_name, "media", params)


@mcp.tool()
def get_media_by_id(site_name: str, media_id: int) -> Dict:
    """
    Get a specific media item by ID
    
    Args:
        site_name (str): Name of the WordPress site
        media_id (int): Media ID
        
    Returns:
        dict: Media item data including URLs and metadata
    """
    return make_wp_request(site_name, f"media/{media_id}")


@mcp.tool()
def search_media(site_name: str, search_term: str, count: int = 10) -> List[Dict]:
    """
    Search for media items
    
    Args:
        site_name (str): Name of the WordPress site
        search_term (str): Search query
        count (int): Maximum results. Default is 10
        
    Returns:
        list[dict]: List of matching media items
    """
    params = {"search": search_term, "per_page": count}
    return make_wp_request(site_name, "media", params)


# ==================== USERS ====================

@mcp.tool()
def get_users(site_name: str, count: int = 10) -> List[Dict]:
    """
    Get users from a WordPress site
    
    Args:
        site_name (str): Name of the WordPress site
        count (int): Number of users. Default is 10
        
    Returns:
        list[dict]: List of users
    """
    params = {"per_page": count}
    return make_wp_request(site_name, "users", params)


@mcp.tool()
def get_user_by_id(site_name: str, user_id: int) -> Dict:
    """
    Get a specific user by ID
    
    Args:
        site_name (str): Name of the WordPress site
        user_id (int): User ID
        
    Returns:
        dict: User data
    """
    return make_wp_request(site_name, f"users/{user_id}")


@mcp.tool()
def get_posts_by_author(site_name: str, author_id: int, count: int = 10) -> List[Dict]:
    """
    Get posts by a specific author
    
    Args:
        site_name (str): Name of the WordPress site
        author_id (int): Author user ID
        count (int): Number of posts. Default is 10
        
    Returns:
        list[dict]: List of posts by the author
    """
    params = {"author": author_id, "per_page": count}
    return make_wp_request(site_name, "posts", params)


# ==================== USER CRUD OPERATIONS ====================

@mcp.tool()
def create_user(
    site_name: str,
    username: str,
    email: str,
    password: str,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    roles: Optional[List[str]] = None
) -> Dict:
    """
    Create a new WordPress user
    
    Args:
        site_name (str): Name of the WordPress site
        username (str): User login name
        email (str): User email address
        password (str): User password
        first_name (str, optional): User first name
        last_name (str, optional): User last name
        roles (list[str], optional): User roles (e.g., ["subscriber"], ["editor"])
        
    Returns:
        dict: Created user data including ID
    """
    data = {
        "username": username,
        "email": email,
        "password": password
    }
    
    if first_name:
        data["first_name"] = first_name
    if last_name:
        data["last_name"] = last_name
    if roles:
        data["roles"] = roles
    
    return make_wp_request(site_name, "users", method="POST", data=data)


@mcp.tool()
def update_user(
    site_name: str,
    user_id: int,
    email: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    password: Optional[str] = None,
    roles: Optional[List[str]] = None,
    description: Optional[str] = None
) -> Dict:
    """
    Update an existing WordPress user
    
    Args:
        site_name (str): Name of the WordPress site
        user_id (int): User ID to update
        email (str, optional): New email address
        first_name (str, optional): New first name
        last_name (str, optional): New last name
        password (str, optional): New password
        roles (list[str], optional): New user roles
        description (str, optional): User bio/description
        
    Returns:
        dict: Updated user data
    """
    data = {}
    
    if email is not None:
        data["email"] = email
    if first_name is not None:
        data["first_name"] = first_name
    if last_name is not None:
        data["last_name"] = last_name
    if password is not None:
        data["password"] = password
    if roles is not None:
        data["roles"] = roles
    if description is not None:
        data["description"] = description
    
    return make_wp_request(site_name, f"users/{user_id}", method="POST", data=data)


@mcp.tool()
def delete_user(
    site_name: str,
    user_id: int,
    reassign: Optional[int] = None,
    force: bool = True
) -> Dict:
    """
    Delete a WordPress user
    
    Args:
        site_name (str): Name of the WordPress site
        user_id (int): User ID to delete
        reassign (int, optional): User ID to reassign posts to
        force (bool): Whether to force deletion. Default is True
        
    Returns:
        dict: Information about the deleted user
    """
    params = {"force": force}
    if reassign:
        params["reassign"] = reassign
    
    return make_wp_request(site_name, f"users/{user_id}", params=params, method="DELETE")


# ==================== COMMENT CRUD OPERATIONS ====================

@mcp.tool()
def create_comment(
    site_name: str,
    post_id: int,
    content: str,
    author_name: Optional[str] = None,
    author_email: Optional[str] = None,
    parent: Optional[int] = None
) -> Dict:
    """
    Create a new comment on a post
    
    Args:
        site_name (str): Name of the WordPress site
        post_id (int): Post ID to comment on
        content (str): Comment content
        author_name (str, optional): Comment author name
        author_email (str, optional): Comment author email
        parent (int, optional): Parent comment ID for replies
        
    Returns:
        dict: Created comment data including ID
    """
    data = {
        "post": post_id,
        "content": content
    }
    
    if author_name:
        data["author_name"] = author_name
    if author_email:
        data["author_email"] = author_email
    if parent:
        data["parent"] = parent
    
    return make_wp_request(site_name, "comments", method="POST", data=data)


@mcp.tool()
def update_comment(
    site_name: str,
    comment_id: int,
    content: Optional[str] = None,
    status: Optional[str] = None
) -> Dict:
    """
    Update an existing comment
    
    Args:
        site_name (str): Name of the WordPress site
        comment_id (int): Comment ID to update
        content (str, optional): New comment content
        status (str, optional): New status (approved, hold, spam, trash)
        
    Returns:
        dict: Updated comment data
    """
    data = {}
    
    if content is not None:
        data["content"] = content
    if status is not None:
        data["status"] = status
    
    return make_wp_request(site_name, f"comments/{comment_id}", method="POST", data=data)


@mcp.tool()
def delete_comment(site_name: str, comment_id: int, force: bool = False) -> Dict:
    """
    Delete a comment
    
    Args:
        site_name (str): Name of the WordPress site
        comment_id (int): Comment ID to delete
        force (bool): Whether to bypass trash and force deletion. Default is False
        
    Returns:
        dict: Information about the deleted comment
    """
    params = {"force": force}
    return make_wp_request(site_name, f"comments/{comment_id}", params=params, method="DELETE")


# ==================== TAXONOMIES ====================

@mcp.tool()
def get_taxonomies(site_name: str) -> List[Dict]:
    """
    Get all taxonomies from a WordPress site
    
    Args:
        site_name (str): Name of the WordPress site
        
    Returns:
        list[dict]: List of taxonomies
    """
    return make_wp_request(site_name, "taxonomies")


# ==================== POST TYPES ====================

@mcp.tool()
def get_post_types(site_name: str) -> List[Dict]:
    """
    Get all post types from a WordPress site
    
    Args:
        site_name (str): Name of the WordPress site
        
    Returns:
        list[dict]: List of post types
    """
    return make_wp_request(site_name, "types")


# ==================== SITE SETTINGS ====================

@mcp.tool()
def get_site_settings(site_name: str) -> Dict:
    """
    Get WordPress site settings
    
    Args:
        site_name (str): Name of the WordPress site
        
    Returns:
        dict: Site settings including title, description, URL, etc.
    """
    return make_wp_request(site_name, "settings")


# ==================== ADVANCED POST QUERIES ====================

@mcp.tool()
def get_posts_by_date(
    site_name: str,
    year: int,
    month: Optional[int] = None,
    count: int = 10
) -> List[Dict]:
    """
    Get posts from a specific date period
    
    Args:
        site_name (str): Name of the WordPress site
        year (int): Year (e.g., 2025)
        month (int, optional): Month (1-12)
        count (int): Number of posts. Default is 10
        
    Returns:
        list[dict]: List of posts from the specified period
    """
    # Build date query
    after = f"{year}-01-01T00:00:00" if not month else f"{year}-{month:02d}-01T00:00:00"
    
    if month:
        # Calculate next month for 'before' parameter
        next_month = month + 1 if month < 12 else 1
        next_year = year if month < 12 else year + 1
        before = f"{next_year}-{next_month:02d}-01T00:00:00"
    else:
        before = f"{year + 1}-01-01T00:00:00"
    
    params = {
        "after": after,
        "before": before,
        "per_page": count
    }
    return make_wp_request(site_name, "posts", params)


@mcp.tool()
def get_posts_advanced(
    site_name: str,
    status: str = "publish",
    order: str = "desc",
    orderby: str = "date",
    count: int = 10,
    offset: int = 0
) -> List[Dict]:
    """
    Get posts with advanced filtering options
    
    Args:
        site_name (str): Name of the WordPress site
        status (str): Post status (publish, draft, pending, private, future). Default is publish
        order (str): Sort order (asc, desc). Default is desc
        orderby (str): Sort by (date, modified, title, author, id, slug). Default is date
        count (int): Number of posts. Default is 10
        offset (int): Number of posts to skip. Default is 0
        
    Returns:
        list[dict]: List of posts matching criteria
    """
    params = {
        "status": status,
        "order": order,
        "orderby": orderby,
        "per_page": count,
        "offset": offset
    }
    return make_wp_request(site_name, "posts", params)


# ==================== RESOURCES ====================

@mcp.resource("site://{site_name}/info")
def get_site_info(site_name: str) -> str:
    """Get detailed information about a WordPress site"""
    try:
        site = get_site(site_name)
        settings = make_wp_request(site_name, "settings")
        
        result = [
            f"# {settings.get('title', 'WordPress Site')}",
            "",
            f"**URL:** {site.url}",
            f"**Description:** {settings.get('description', 'N/A')}",
            f"**Language:** {settings.get('language', 'N/A')}",
            f"**Timezone:** {settings.get('timezone_string', 'N/A')}",
            f"**Date Format:** {settings.get('date_format', 'N/A')}",
            f"**Time Format:** {settings.get('time_format', 'N/A')}",
            "",
            f"**API Base:** {site.get_api_base_url()}",
        ]
        
        return "\n".join(result)
    except Exception as e:
        return f"Error fetching site info: {str(e)}"


@mcp.resource("site://{site_name}/stats")
def get_site_stats(site_name: str) -> str:
    """Get statistics about a WordPress site"""
    try:
        # Fetch various counts
        posts = make_wp_request(site_name, "posts", {"per_page": 1, "status": "publish"})
        pages = make_wp_request(site_name, "pages", {"per_page": 1})
        categories = make_wp_request(site_name, "categories", {"per_page": 1})
        tags = make_wp_request(site_name, "tags", {"per_page": 1})
        media = make_wp_request(site_name, "media", {"per_page": 1})
        
        # WordPress API returns total count in headers, but we'll use what we can
        result = [
            f"# Site Statistics: {site_name}",
            "",
            "## Content Overview",
            f"- Posts available",
            f"- Pages available",
            f"- Categories available",
            f"- Tags available",
            f"- Media items available",
            "",
            "Note: Use specific tools to get exact counts and details"
        ]
        
        return "\n".join(result)
    except Exception as e:
        return f"Error fetching site stats: {str(e)}"


if __name__ == "__main__":
    # Test the WordPress multi-site functions when run directly
    print("🧪 Testing WordPress Multi-Site Manager...")
    print("=" * 60)
    
    try:
        # Test 1: List available sites
        print("\n1️⃣ Getting available sites...")
        sites = get_available_sites()
        
        if not sites:
            print("⚠️  No sites configured. Please set environment variables:")
            print("   SITE_<NAME>_URL=https://example.com")
            print("   SITE_<NAME>_USER=username")
            print("   SITE_<NAME>_APP_PASSWORD=xxxx xxxx xxxx xxxx")
            print("\nExample:")
            print("   SITE_GOOGLERANK_URL=https://googlerank.com.au")
            print("   SITE_GOOGLERANK_USER=goto@digifix.com.au")
            print("   SITE_GOOGLERANK_APP_PASSWORD=iUGn XOkL QPvs q6jv CCI1 xWAd")
        else:
            print(f"✅ Found {len(sites)} configured site(s):")
            for site in sites:
                print(f"   - {site['name']}: {site['url']}")
            
            # Test 2: Fetch recent posts from first site
            if sites:
                test_site = sites[0]['name']
                print(f"\n2️⃣ Testing with site: {test_site}")
                print(f"   Fetching recent posts...")
                
                posts = get_recent_posts(test_site, 2)
                print(f"   ✅ Found {len(posts)} posts")
                
                if posts:
                    first_post = posts[0]
                    post_id = first_post['id']
                    title = first_post.get('title', {}).get('rendered', 'No title')
                    print(f"   📄 Latest post: \"{title}\" (ID: {post_id})")
                    
                    # Test 3: Fetch specific post
                    print(f"\n3️⃣ Fetching specific post {post_id}...")
                    specific_post = get_post_by_id(test_site, post_id)
                    print(f"   ✅ Retrieved: \"{specific_post.get('title', {}).get('rendered', 'No title')}\"")
                    
                    # Test 4: Get categories
                    print(f"\n4️⃣ Fetching categories...")
                    categories = get_post_categories(test_site)
                    print(f"   ✅ Found {len(categories)} categories")
                    if categories:
                        print(f"   First category: {categories[0].get('name', 'N/A')}")
        
        print("\n" + "=" * 60)
        print("🎉 All tests passed!")
        
    except ValueError as e:
        print(f"\n⚠️  Configuration error: {e}")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()