"""
FastMCP quickstart example.

cd to the `examples/snippets/clients` directory and run:
    uv run server fastmcp_quickstart stdio
"""

from mcp.server.fastmcp import FastMCP
from utils.wordpress import util_get_post_by_id, util_get_recent_posts


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
    return util_get_post_by_id(post_id)

@mcp.tool()
def get_recent_posts(count: int = 5) -> list[dict]:
    """
    Fetch recent WordPress posts.
    Args:
        count (int): Number of recent posts to fetch. Default is 5.
    Returns:
        list[dict]: A list of recent WordPress post data.
    """
    return util_get_recent_posts(count)


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