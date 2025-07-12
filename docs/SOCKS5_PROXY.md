# SOCKS5 Proxy Feature

This document describes the new SOCKS5 proxy functionality added to sysbot.

## Overview

The SOCKS5 proxy feature allows you to create a local SOCKS5 proxy server that forwards traffic through a chain of SSH tunnels. This is useful for:

- Accessing services through multiple SSH hops
- Creating secure tunnels for HTTP/HTTPS traffic
- Bypassing network restrictions through SSH tunneling
- Providing a SOCKS5 proxy for applications that support it

## Features

- **Multiple SSH Hops**: Support for chaining through multiple SSH servers
- **Configurable Listen Port**: Choose any available local port for the SOCKS5 proxy
- **Automatic Tunnel Management**: Automatically creates and manages SSH tunnel chains
- **Clean Shutdown**: Proper cleanup of all connections and tunnels
- **Thread-Safe**: Handles multiple concurrent connections

## API

### open_proxy_sock5(alias, listen_port, tunnel_config)

Opens a SOCKS5 proxy server.

**Parameters:**
- `alias` (str): Unique identifier for this proxy session
- `listen_port` (int): Local port to listen for SOCKS5 connections  
- `tunnel_config` (list or JSON string): SSH tunnel configuration

**Returns:**
- Dict with status, listen_port, session_alias, and tunnel_count

### close_proxy_sock5(alias)

Closes a SOCKS5 proxy server and cleans up resources.

**Parameters:**
- `alias` (str): The proxy session alias to close

**Returns:**
- Dict with status and session_alias

## Usage Examples

### Single SSH Hop

```python
from sysbot.connectors import ConnectorHandler

handler = ConnectorHandler()

# Single SSH hop configuration
tunnel_config = [
    {
        'ip': '192.168.1.100',
        'port': 22,
        'username': 'user1',
        'password': 'password1'
    }
]

# Start SOCKS5 proxy on port 8080
result = handler.open_proxy_sock5(
    alias='my_proxy',
    listen_port=8080,
    tunnel_config=tunnel_config
)

print(f"SOCKS5 proxy started: {result}")
# Output: SOCKS5 proxy started: {'status': 'started', 'listen_port': 8080, 'session_alias': 'my_proxy', 'tunnel_count': 0}

# Configure your applications to use SOCKS5 proxy at 127.0.0.1:8080

# Close the proxy when done
result = handler.close_proxy_sock5('my_proxy')
print(f"Proxy closed: {result}")
```

### Multiple SSH Hops

```python
from sysbot.connectors import ConnectorHandler

handler = ConnectorHandler()

# Multiple SSH hops configuration
tunnel_config = [
    {
        'ip': '192.168.1.100',  # First SSH hop
        'port': 22,
        'username': 'user1',
        'password': 'password1'
    },
    {
        'ip': '10.0.0.50',      # Second SSH hop (accessible from first hop)
        'port': 22,
        'username': 'user2',
        'password': 'password2'
    },
    {
        'ip': '172.16.0.10',    # Third SSH hop (accessible from second hop)
        'port': 22,
        'username': 'user3',
        'password': 'password3'
    }
]

# Start SOCKS5 proxy with multiple hops
result = handler.open_proxy_sock5(
    alias='multi_hop_proxy',
    listen_port=9090,
    tunnel_config=tunnel_config
)

print(f"Multi-hop SOCKS5 proxy started: {result}")
# Output: Multi-hop SOCKS5 proxy started: {'status': 'started', 'listen_port': 9090, 'session_alias': 'multi_hop_proxy', 'tunnel_count': 2}

# Close when done
handler.close_proxy_sock5('multi_hop_proxy')
```

### JSON Configuration

```python
import json
from sysbot.connectors import ConnectorHandler

handler = ConnectorHandler()

# JSON string configuration
tunnel_config_json = json.dumps([
    {
        'ip': '192.168.1.100',
        'port': 22,
        'username': 'user1',
        'password': 'password1'
    },
    {
        'ip': '10.0.0.50',
        'port': 22,
        'username': 'user2',
        'password': 'password2'
    }
])

# Start SOCKS5 proxy with JSON config
result = handler.open_proxy_sock5(
    alias='json_proxy',
    listen_port=7070,
    tunnel_config=tunnel_config_json
)
```

## Configuration Format

The `tunnel_config` parameter accepts a list of dictionaries, where each dictionary represents an SSH hop:

```python
{
    'ip': 'hostname_or_ip',      # SSH server hostname or IP address
    'port': 22,                  # SSH server port (usually 22)
    'username': 'ssh_username',  # SSH username
    'password': 'ssh_password'   # SSH password
}
```

## Using the SOCKS5 Proxy

Once the SOCKS5 proxy is running, configure your applications to use it:

### curl
```bash
curl --socks5 127.0.0.1:8080 http://example.com
```

### Firefox
1. Go to Settings > Network Settings
2. Select "Manual proxy configuration"
3. Set SOCKS Host: `127.0.0.1`, Port: `8080`
4. Select "SOCKS v5"

### Python requests with PySocks
```python
import requests

proxies = {
    'http': 'socks5://127.0.0.1:8080',
    'https': 'socks5://127.0.0.1:8080'
}

response = requests.get('http://example.com', proxies=proxies)
```

## Implementation Details

The SOCKS5 proxy implementation:

1. **Tunnel Chain Creation**: Uses `sshtunnel` to create a chain of SSH tunnels
2. **SOCKS5 Server**: Implements a basic SOCKS5 server that listens on the specified port
3. **Connection Handling**: Each SOCKS5 connection is handled in a separate thread
4. **Data Relay**: Traffic is forwarded between SOCKS5 clients and SSH channels
5. **Resource Management**: Proper cleanup of sockets, channels, and tunnels

## Error Handling

The implementation includes comprehensive error handling:

- Invalid tunnel configurations
- SSH connection failures
- Port binding issues
- Network timeouts
- Resource cleanup on failures

## Security Considerations

- SSH credentials are passed in configuration - ensure secure handling
- SOCKS5 proxy runs on localhost only (127.0.0.1)
- No authentication is required for SOCKS5 connections (suitable for local use)
- SSH tunnels provide encryption for all forwarded traffic

## Limitations

- Currently supports password authentication only (no key-based auth yet)
- SOCKS5 proxy binds to localhost only
- No SOCKS5 authentication implemented
- IPv6 addresses not supported in SOCKS5 protocol implementation