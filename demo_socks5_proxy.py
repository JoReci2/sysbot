#!/usr/bin/env python3
"""
SOCKS5 Proxy Demonstration Script

This script demonstrates the new SOCKS5 proxy functionality.
It shows how to:
1. Create a SOCKS5 proxy with SSH tunnel chaining
2. Configure the proxy for different scenarios
3. Properly manage proxy lifecycle

Usage:
    python demo_socks5_proxy.py

Note: Update the SSH credentials in the script before running.
"""

import time
import json
from sysbot.connectors import ConnectorHandler


def demo_basic_socks5_proxy():
    """Demonstrate basic SOCKS5 proxy functionality."""
    print("=" * 60)
    print("DEMO: Basic SOCKS5 Proxy")
    print("=" * 60)
    
    handler = ConnectorHandler()
    
    # Example configuration - replace with your actual SSH details
    tunnel_config = [
        {
            'ip': '127.0.0.1',  # Replace with your SSH server IP
            'port': 22,
            'username': 'demo_user',  # Replace with actual username
            'password': 'demo_pass'   # Replace with actual password
        }
    ]
    
    try:
        print("📡 Starting SOCKS5 proxy on port 8080...")
        result = handler.open_proxy_sock5(
            alias='demo_proxy',
            listen_port=8080,
            tunnel_config=tunnel_config
        )
        
        print(f"✅ Proxy started successfully:")
        print(f"   Status: {result['status']}")
        print(f"   Listen Port: {result['listen_port']}")
        print(f"   Session Alias: {result['session_alias']}")
        print(f"   Tunnel Count: {result['tunnel_count']}")
        print()
        print("🔗 SOCKS5 proxy is now running at 127.0.0.1:8080")
        print("   You can configure applications to use this proxy")
        print()
        print("📝 Example usage:")
        print("   curl --socks5 127.0.0.1:8080 http://httpbin.org/ip")
        print("   # This would show the IP of your SSH server")
        print()
        
        # Keep running for demonstration
        print("⏱️  Proxy will run for 10 seconds for demonstration...")
        time.sleep(10)
        
    except Exception as e:
        print(f"❌ Error starting proxy: {e}")
        print("💡 Make sure to update SSH credentials in the script")
    finally:
        try:
            print("🔚 Closing SOCKS5 proxy...")
            result = handler.close_proxy_sock5('demo_proxy')
            print(f"✅ Proxy closed: {result['status']}")
        except Exception as e:
            print(f"⚠️  Error closing proxy: {e}")


def demo_multi_hop_socks5_proxy():
    """Demonstrate SOCKS5 proxy with multiple SSH hops."""
    print("\n" + "=" * 60)
    print("DEMO: Multi-Hop SOCKS5 Proxy")
    print("=" * 60)
    
    handler = ConnectorHandler()
    
    # Multi-hop configuration - replace with your actual servers
    tunnel_config = [
        {
            'ip': '192.168.1.10',   # First SSH hop
            'port': 22,
            'username': 'user1',
            'password': 'pass1'
        },
        {
            'ip': '10.0.0.20',      # Second SSH hop (accessible from first)
            'port': 22,
            'username': 'user2',
            'password': 'pass2'
        }
    ]
    
    try:
        print("📡 Starting multi-hop SOCKS5 proxy on port 9090...")
        print(f"   Tunnel chain: {tunnel_config[0]['ip']} → {tunnel_config[1]['ip']}")
        
        result = handler.open_proxy_sock5(
            alias='multi_hop_demo',
            listen_port=9090,
            tunnel_config=tunnel_config
        )
        
        print(f"✅ Multi-hop proxy started successfully:")
        print(f"   Status: {result['status']}")
        print(f"   Listen Port: {result['listen_port']}")
        print(f"   Tunnel Count: {result['tunnel_count']}")
        print()
        print("🔗 Multi-hop SOCKS5 proxy is now running at 127.0.0.1:9090")
        print("   Traffic will be routed through 2 SSH servers")
        print()
        
        # Keep running for demonstration
        print("⏱️  Proxy will run for 10 seconds for demonstration...")
        time.sleep(10)
        
    except Exception as e:
        print(f"❌ Error starting multi-hop proxy: {e}")
        print("💡 Make sure SSH servers are accessible and credentials are correct")
    finally:
        try:
            print("🔚 Closing multi-hop SOCKS5 proxy...")
            result = handler.close_proxy_sock5('multi_hop_demo')
            print(f"✅ Proxy closed: {result['status']}")
        except Exception as e:
            print(f"⚠️  Error closing proxy: {e}")


def demo_json_config():
    """Demonstrate SOCKS5 proxy with JSON configuration."""
    print("\n" + "=" * 60)
    print("DEMO: SOCKS5 Proxy with JSON Configuration")
    print("=" * 60)
    
    handler = ConnectorHandler()
    
    # JSON configuration
    tunnel_config_dict = [
        {
            'ip': '127.0.0.1',
            'port': 22,
            'username': 'demo_user',
            'password': 'demo_pass'
        }
    ]
    
    tunnel_config_json = json.dumps(tunnel_config_dict, indent=2)
    
    print("📋 Using JSON configuration:")
    print(tunnel_config_json)
    print()
    
    try:
        print("📡 Starting SOCKS5 proxy with JSON config on port 7070...")
        
        result = handler.open_proxy_sock5(
            alias='json_demo',
            listen_port=7070,
            tunnel_config=tunnel_config_json
        )
        
        print(f"✅ Proxy with JSON config started successfully:")
        print(f"   Status: {result['status']}")
        print(f"   Listen Port: {result['listen_port']}")
        print()
        
        # Keep running for demonstration
        print("⏱️  Proxy will run for 5 seconds for demonstration...")
        time.sleep(5)
        
    except Exception as e:
        print(f"❌ Error starting proxy with JSON config: {e}")
    finally:
        try:
            print("🔚 Closing JSON-configured SOCKS5 proxy...")
            result = handler.close_proxy_sock5('json_demo')
            print(f"✅ Proxy closed: {result['status']}")
        except Exception as e:
            print(f"⚠️  Error closing proxy: {e}")


def demo_error_handling():
    """Demonstrate error handling scenarios."""
    print("\n" + "=" * 60)
    print("DEMO: Error Handling")
    print("=" * 60)
    
    handler = ConnectorHandler()
    
    # Test with invalid configuration
    print("🧪 Testing error handling with invalid configuration...")
    
    try:
        # Empty tunnel config
        result = handler.open_proxy_sock5(
            alias='error_test',
            listen_port=6060,
            tunnel_config=[]
        )
    except Exception as e:
        print(f"✅ Correctly caught empty config error: {e}")
    
    try:
        # Invalid JSON
        result = handler.open_proxy_sock5(
            alias='error_test',
            listen_port=6060,
            tunnel_config="invalid json {"
        )
    except Exception as e:
        print(f"✅ Correctly caught JSON parsing error: {e}")
    
    try:
        # Close non-existent proxy
        result = handler.close_proxy_sock5('non_existent')
    except Exception as e:
        print(f"✅ Correctly caught non-existent proxy error: {e}")
    
    print("✅ Error handling tests completed successfully")


def show_usage_examples():
    """Show practical usage examples."""
    print("\n" + "=" * 60)
    print("PRACTICAL USAGE EXAMPLES")
    print("=" * 60)
    
    print("1️⃣  Testing with curl:")
    print("   curl --socks5 127.0.0.1:8080 http://httpbin.org/ip")
    print()
    
    print("2️⃣  Python requests with SOCKS5:")
    print("   import requests")
    print("   proxies = {'http': 'socks5://127.0.0.1:8080',")
    print("            'https': 'socks5://127.0.0.1:8080'}")
    print("   response = requests.get('http://example.com', proxies=proxies)")
    print()
    
    print("3️⃣  Firefox configuration:")
    print("   - Settings > Network Settings")
    print("   - Manual proxy configuration")
    print("   - SOCKS Host: 127.0.0.1, Port: 8080")
    print("   - Select SOCKS v5")
    print()
    
    print("4️⃣  SSH tunnel through SOCKS5:")
    print("   ssh -o ProxyCommand='nc -X 5 -x 127.0.0.1:8080 %h %p' user@target")
    print()


def main():
    """Main demonstration function."""
    print("🚀 SYSBOT SOCKS5 PROXY DEMONSTRATION")
    print("=" * 60)
    print()
    print("This demonstration will show the new SOCKS5 proxy functionality.")
    print("⚠️  IMPORTANT: Update SSH credentials in this script before running!")
    print()
    
    # Basic demo
    demo_basic_socks5_proxy()
    
    # Multi-hop demo (commented out as it requires multiple servers)
    # demo_multi_hop_socks5_proxy()
    
    # JSON config demo
    demo_json_config()
    
    # Error handling demo
    demo_error_handling()
    
    # Usage examples
    show_usage_examples()
    
    print("\n" + "=" * 60)
    print("✅ DEMONSTRATION COMPLETED")
    print("=" * 60)
    print()
    print("📖 For more information, see:")
    print("   - docs/SOCKS5_PROXY.md")
    print("   - Source: sysbot/connectors/ssh/socks5_proxy.py")
    print()
    print("🎯 Key Features Demonstrated:")
    print("   ✅ Configurable listen port")
    print("   ✅ SSH tunnel chaining")
    print("   ✅ JSON configuration support")
    print("   ✅ Proper error handling")
    print("   ✅ Clean resource management")


if __name__ == "__main__":
    main()