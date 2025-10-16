"""
HTTP/SSE Server for WordPress MCP
Wraps the MCP server to be accessible over HTTP using Server-Sent Events (SSE)
"""

from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import Response, JSONResponse
import uvicorn
import asyncio
from main import mcp, load_wordpress_sites

# Create SSE transport
sse = SseServerTransport("/messages")

async def handle_sse(request):
    """Handle SSE connections for MCP"""
    async with sse.connect_sse(
        request.scope, request.receive, request._send
    ) as streams:
        await mcp.run(
            streams[0], streams[1], mcp.create_initialization_options()
        )

async def handle_messages(request):
    """Handle message posting"""
    await sse.handle_post_message(request.scope, request.receive, request._send)
    return Response()

async def handle_health(request):
    """Health check endpoint for monitoring"""
    try:
        sites = load_wordpress_sites()
        return JSONResponse({
            "status": "healthy",
            "server": mcp.name,
            "sites_configured": len(sites),
            "site_names": list(sites.keys())
        })
    except Exception as e:
        return JSONResponse({
            "status": "unhealthy",
            "error": str(e)
        }, status_code=500)

async def handle_root(request):
    """Root endpoint with server info"""
    return JSONResponse({
        "name": "WordPress Multi-Site MCP Server",
        "version": "1.0.0",
        "transport": "sse",
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
    uvicorn.run(app, host="0.0.0.0", port=8000)
