#!/usr/bin/env python3
"""
Verify MCP installation for Claude Desktop
"""
import json
import os
from pathlib import Path

def check_claude_config():
    """Check Claude's MCP server configuration"""
    config_path = Path.home() / "Library/Application Support/Claude/claude_desktop_config.json"
    
    if not config_path.exists():
        print("❌ Claude config file not found")
        return False
    
    with open(config_path) as f:
        config = json.load(f)
    
    servers = config.get("mcpServers", {})
    
    # Check for the new server name
    server_name = "WordPress Multi-Site Manager"
    if server_name not in servers:
        print(f"❌ '{server_name}' server not found in Claude config")
        return False
    
    demo_config = servers[server_name]
    print(f"✅ '{server_name}' server found in Claude config")
    print(f"   Command: {demo_config['command']}")
    print(f"   Args: {' '.join(demo_config['args'])}")
    
    # Check if required packages are included
    args = demo_config.get("args", [])
    has_requests = "--with" in args and "requests" in args
    has_dotenv = "--with" in args and "python-dotenv" in args
    has_env_file = "--env-file" in args
    
    if has_requests:
        print("✅ 'requests' package is included")
    else:
        print("❌ 'requests' package is NOT included")
    
    if has_dotenv:
        print("✅ 'python-dotenv' package is included")
    else:
        print("❌ 'python-dotenv' package is NOT included")
    
    if has_env_file:
        print("✅ '.env' file is configured")
    else:
        print("⚠️  '.env' file is NOT configured in args")
    
    return has_requests and has_dotenv

def simulate_server_start():
    """Simulate how Claude would start the server"""
    print("\n🔍 Testing if server can import required modules...")
    
    try:
        # This simulates what happens when Claude starts the server
        import sys
        import importlib.util
        
        spec = importlib.util.spec_from_file_location("main", "main.py")
        if spec is None or spec.loader is None:
            print("❌ Could not load main.py")
            return False
            
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        print("✅ main.py loaded successfully")
        print(f"✅ MCP server name: {module.mcp.name}")
        
        # Test site loading
        sites = module.load_wordpress_sites()
        print(f"✅ Found {len(sites)} configured WordPress site(s)")
        for name, site in sites.items():
            print(f"   - {name}: {site.url}")
        
        if not sites:
            print("⚠️  No sites configured in .env file")
            print("   Add sites using: SITE_<NAME>_URL, SITE_<NAME>_USER, SITE_<NAME>_APP_PASSWORD")
        
        return True
        
    except ModuleNotFoundError as e:
        print(f"❌ Missing module: {e}")
        print("   This is likely why the server is failing")
        return False
    except Exception as e:
        print(f"❌ Error loading main.py: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🔍 MCP Installation Verification")
    print("=" * 60)
    
    config_ok = check_claude_config()
    server_ok = simulate_server_start()
    
    print("\n" + "=" * 60)
    
    if config_ok and server_ok:
        print("✅ Everything looks good!")
        print("\nNext steps:")
        print("1. Completely quit Claude (Cmd+Q)")
        print("2. Restart Claude")
        print("3. The 'WordPress Multi-Site Manager' MCP server should now be available")
    else:
        print("❌ There are issues that need to be fixed")
        if not config_ok:
            print("\n⚠️  Run this command to fix:")
            print("   cd /Users/shakil/Dev/learn/mcp/mcp-server-demo")
            print("   uv run mcp install main.py --with requests --with python-dotenv --env-file .env")

if __name__ == "__main__":
    main()
