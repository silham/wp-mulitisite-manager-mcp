"""
FastMCP quickstart example.

cd to the `examples/snippets/clients` directory and run:
    uv run server fastmcp_quickstart stdio
"""

from mcp.server.fastmcp import FastMCP
from wp_api import WPClient
from wp_api.auth import ApplicationPasswordAuth

def get_wp_client() -> WPClient:
    """Get a WordPress client instance."""
    auth = ApplicationPasswordAuth( username="goto@digifix.com.au", app_password="iUGn XOkL QPvs q6jv CCI1 xWAd")
    return WPClient(base_url="https://googlerank.com.au", auth=auth)


# Create an MCP server
mcp = FastMCP("Demo")


@mcp.tool()
def get_post_by_id(post_id: int) -> dict:
    """
    Fetch a WordPress post by its ID
    Args:
        post_id (int): The ID of the WordPress post.
    Returns:
        dict: The WordPress post data.
    """
    wp = get_wp_client()
    return wp.posts.get(post_id)

@mcp.tool()
def get_recent_posts(count: int = 5) -> list[dict]:
    """
    Fetch recent WordPress posts.
    Args:
        count (int): Number of recent posts to fetch. Default is 5.
    Returns:
        list[dict]: A list of recent WordPress post data.
    """
    wp = get_wp_client()
    return wp.posts.list(per_page=count)


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"


# Add a prompt
@mcp.prompt()
def greet_user(name: str, style: str = "friendly") -> str:
    """Generate a greeting prompt"""
    styles = {
        "friendly": "Please write a warm, friendly greeting",
        "formal": "Please write a formal, professional greeting",
        "casual": "Please write a casual, relaxed greeting",
    }

    return f"{styles.get(style, styles['friendly'])} for someone named {name}."