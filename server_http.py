"""
HTTP/SSE Server for WordPress MCP
Wraps the MCP server to be accessible over HTTP using Server-Sent Events (SSE)
with authentication support
"""

from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import Response, JSONResponse
from typing import Optional, Tuple
import uvicorn
import asyncio
import os
from main import mcp, load_wordpress_sites

# Load authentication token from environment
AUTH_TOKEN = os.getenv("MCP_AUTH_TOKEN")

# Create SSE transport
sse = SseServerTransport("/messages")

def check_auth(request) -> Tuple[bool, Optional[JSONResponse]]:
    """Check authentication token from request headers"""
    if not AUTH_TOKEN:
        # No auth token configured, allow access
        return True, None
    
    # Check Authorization header
    auth_header = request.headers.get("Authorization", "")
    
    # Support both "Bearer TOKEN" and "TOKEN" formats
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
    else:
        token = auth_header
    
    if token != AUTH_TOKEN:
        return False, JSONResponse(
            {"error": "Unauthorized", "message": "Invalid or missing authentication token"},
            status_code=401,
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return True, None

async def handle_sse(request):
    """Handle SSE connections for MCP"""
    # Check authentication
    authorized, error_response = check_auth(request)
    if not authorized:
        return error_response
    
    async with sse.connect_sse(
        request.scope, request.receive, request._send
    ) as streams:
        await mcp._mcp_server.run(
            streams[0], 
            streams[1], 
            mcp._mcp_server.create_initialization_options()
        )

async def handle_messages(request):
    """Handle message posting"""
    # Check authentication
    authorized, error_response = check_auth(request)
    if not authorized:
        return error_response
    
    await sse.handle_post_message(request.scope, request.receive, request._send)
    return Response()

async def handle_health(request):
    """Health check endpoint for monitoring (no auth required)"""
    try:
        sites = load_wordpress_sites()
        auth_enabled = AUTH_TOKEN is not None
        return JSONResponse({
            "status": "healthy",
            "server": mcp.name,
            "sites_configured": len(sites),
            "site_names": list(sites.keys()),
            "auth_enabled": auth_enabled
        })
    except Exception as e:
        return JSONResponse({
            "status": "unhealthy",
            "error": str(e)
        }, status_code=500)

async def handle_root(request):
    """Root endpoint with server info (no auth required)"""
    auth_enabled = AUTH_TOKEN is not None
    return JSONResponse({
        "name": "WordPress Multi-Site MCP Server",
        "version": "1.0.0",
        "transport": "sse",
        "auth_enabled": auth_enabled,
        "endpoints": {
            "sse": "/sse",
            "messages": "/messages",
            "health": "/health"
        },
        "documentation": "https://github.com/silham/learn-mcp"
    })

# Create Starlette app
app = Starlette(
    routes=[
        Route("/", endpoint=handle_root),
        Route("/health", endpoint=handle_health),
        Route("/sse", endpoint=handle_sse),
        Route("/messages", endpoint=handle_messages, methods=["POST"]),
    ]
)

if __name__ == "__main__":
    # Run the server
    print("🚀 Starting WordPress MCP Server on http://0.0.0.0:8000")
    print("📡 SSE endpoint: http://0.0.0.0:8000/sse")
    print("🏥 Health check: http://0.0.0.0:8000/health")
    if AUTH_TOKEN:
        print("🔒 Authentication: ENABLED")
        print(f"   Token: {AUTH_TOKEN[:10]}..." if len(AUTH_TOKEN) > 10 else f"   Token: {AUTH_TOKEN}")
    else:
        print("⚠️  Authentication: DISABLED (set MCP_AUTH_TOKEN environment variable to enable)")
    uvicorn.run(app, host="0.0.0.0", port=8000)
