#!/usr/bin/env python3
"""
Test script for the MCP server to help diagnose connection issues.
Run this to test if the server components work properly.
"""

def test_imports():
    """Test that all required modules can be imported."""
    print("🔍 Testing imports...")
    try:
        from mcp.server.fastmcp import FastMCP
        print("✅ FastMCP import successful")
        
        from wp_api import WPClient
        from wp_api.auth import ApplicationPasswordAuth
        print("✅ WordPress API imports successful")
        
        import main
        print("✅ Main module import successful")
        
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_wordpress_connection():
    """Test WordPress client creation and basic connectivity."""
    print("\n🔍 Testing WordPress connection...")
    try:
        from main import get_wp_client
        wp = get_wp_client()
        print(f"✅ WordPress client created: {wp.base_url}")
        
        # Test a simple API call
        from main import get_recent_posts
        posts = get_recent_posts(1)
        print(f"✅ API call successful - fetched {len(posts)} post(s)")
        
        return True
    except Exception as e:
        print(f"❌ WordPress connection failed: {e}")
        return False

def test_mcp_server():
    """Test MCP server creation."""
    print("\n🔍 Testing MCP server...")
    try:
        from main import mcp
        print(f"✅ MCP server created: '{mcp.name}'")
        
        # Check if tools are registered
        tools = getattr(mcp, '_tools', {})
        print(f"✅ Registered tools: {list(tools.keys())}")
        
        return True
    except Exception as e:
        print(f"❌ MCP server creation failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 MCP Server Test Suite")
    print("=" * 50)
    
    all_passed = True
    
    all_passed &= test_imports()
    all_passed &= test_wordpress_connection()
    all_passed &= test_mcp_server()
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! MCP server should work correctly.")
        print("\nIf Claude still shows 'Server disconnected', try:")
        print("1. Restart Claude completely")
        print("2. Check Claude's MCP server logs")
        print("3. Verify network connectivity to WordPress site")
    else:
        print("❌ Some tests failed. Check the errors above.")
    
    return all_passed

if __name__ == "__main__":
    main()