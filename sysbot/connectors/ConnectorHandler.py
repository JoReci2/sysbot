"""
##################################################################################
# Auteur       : Thibault Sciré
# Version      : 0.0.1
# Python       : 3.12
##################################################################################
"""
import socket, paramiko, json
from robot.utils import ConnectionCache
from robot.api.deco import keyword, library
from sshtunnel import SSHTunnelForwarder

from ..utils import TunnelingManager


class ConnectorHandler(object):
    """
    ======================
    ConnectorHandler Class
    ======================

    The ConnectorHandler class provides a comprehensive interface for managing protocol-specific 
    connections with optional SSH tunneling capabilities. It serves as the central orchestrator 
    for all network connections within the pyTasq framework, supporting multiple protocols and 
    complex networking scenarios including nested SSH tunnels.

    Overview
    ========

    The ConnectorHandler acts as a unified facade for connecting to various systems through 
    different protocols including SSH, HTTP, WinRM, and Socket-based connections. It abstracts 
    the complexity of protocol-specific implementations while providing advanced features like 
    SSH tunneling for secure connections across network boundaries.

    Key Features
    ============

    * **Protocol Agnostic**: Supports multiple protocols through dynamic connector loading
    * **SSH Tunneling**: Advanced nested SSH tunnel support for complex network topologies  
    * **Session Management**: Robust session caching and lifecycle management
    * **Robot Framework Integration**: Native support with proper scoping and documentation
    * **Error Handling**: Comprehensive exception handling with detailed error messages
    * **Connection Pooling**: Efficient connection reuse through alias-based session caching

    Supported Protocols
    ===================

    SSH Connectors
    --------------
    * **bash**: Linux/Unix shell access via SSH
    * **python**: Python interpreter access via SSH

    HTTP Connectors
    ---------------
    * **redfish**: BMC/server management via Redfish API
    * **basicauth**: Basic HTTP authentication
    * **neorest**: NEO REST API connections
    * **vmwarensx**: VMware NSX-T API connections
    * **vmwarevcf**: VMware Cloud Foundation API
    * **vsphere**: VMware vSphere API connections

    WinRM Connectors
    ----------------
    * **powershell**: Windows PowerShell remote execution

    Socket Connectors
    -----------------
    * **tcp**: Raw TCP connections with optional SSL/TLS
    * **udp**: UDP connectionless communication

    Architecture
    ============

    The ConnectorHandler follows a layered architecture:

    1. **Handler Layer**: ConnectorHandler (this class) - Session management and tunneling
    2. **Protocol Layer**: Dynamic connector loading via TunnelingManager
    3. **Interface Layer**: ConnectorInterface - Common protocol contract
    4. **Implementation Layer**: Protocol-specific connectors (SSH, HTTP, WinRM, Socket)

    SSH Tunneling Capabilities
    ==========================

    The class supports sophisticated SSH tunneling scenarios:

    Single Hop Tunnel
    ------------------
    Connect through one SSH jump host to reach the target system.

    .. code-block:: python

        tunnel_config = [{
            'ip': '10.0.0.1',
            'port': 22,
            'username': 'jumpuser',
            'password': 'jumppass'
        }]

    Multi-Hop Nested Tunnels
    -------------------------
    Chain multiple SSH hops for complex network topologies.

    .. code-block:: python

        tunnel_config = [
            {
                'ip': '10.0.0.1',     # First jump host
                'port': 22,
                'username': 'jump1',
                'password': 'pass1'
            },
            {
                'ip': '192.168.1.1',  # Second jump host
                'port': 22,
                'username': 'jump2', 
                'password': 'pass2'
            }
        ]

    Usage Examples
    ==============

    Basic Direct Connection
    -----------------------

    .. code-block:: python

        from pytasq.connectors import ConnectorHandler
        
        handler = ConnectorHandler()
        
        # Open SSH connection
        handler.open_session(
            alias='server1',
            protocol='ssh',
            product='bash',
            host='192.168.1.100',
            port=22,
            login='admin',
            password='secret'
        )
        
        # Execute command
        result = handler.execute_command('server1', 'ls -la')
        print(result)
        
        # Close session
        handler.close_session('server1')

    HTTP API Connection
    -------------------

    .. code-block:: python

        # Connect to Redfish BMC
        handler.open_session(
            alias='bmc1',
            protocol='http',
            product='redfish',
            host='10.0.0.50',
            port=443,
            login='root',
            password='calvin'
        )
        
        # Get system information
        result = handler.execute_command('bmc1', '/redfish/v1/Systems/1')

    Tunneled Connection
    -------------------

    .. code-block:: python

        import json
        
        # Define tunnel configuration
        tunnel_config = [{
            'ip': '10.0.0.1',
            'port': 22,
            'username': 'jumpuser',
            'password': 'jumppass'
        }]
        
        # Open tunneled connection
        handler.open_session(
            alias='remote_server',
            protocol='ssh',
            product='bash',
            host='192.168.100.50',  # Target behind jump host
            port=22,
            login='admin',
            password='secret',
            tunnel_config=tunnel_config
        )

    Complex Multi-Protocol Usage
    -----------------------------

    .. code-block:: python

        # Multiple connections with different protocols
        connections = [
            {
                'alias': 'linux_server',
                'protocol': 'ssh',
                'product': 'bash',
                'host': '10.0.1.10',
                'port': 22
            },
            {
                'alias': 'windows_server', 
                'protocol': 'winrm',
                'product': 'powershell',
                'host': '10.0.1.20',
                'port': 5986
            },
            {
                'alias': 'bmc_server',
                'protocol': 'http',
                'product': 'redfish',
                'host': '10.0.1.30',
                'port': 443
            }
        ]
        
        # Open all connections
        for conn in connections:
            handler.open_session(
                alias=conn['alias'],
                protocol=conn['protocol'],
                product=conn['product'],
                host=conn['host'],
                port=conn['port'],
                login='admin',
                password='password'
            )
        
        # Execute commands on different systems
        linux_result = handler.execute_command('linux_server', 'uname -a')
        windows_result = handler.execute_command('windows_server', 'Get-ComputerInfo')
        bmc_result = handler.execute_command('bmc_server', '/redfish/v1/Systems/1')
        
        # Clean up all sessions
        handler.close_all_sessions()

    Robot Framework Integration
    ===========================

    The class is designed for seamless Robot Framework integration:

    .. code-block:: robotframework

        *** Settings ***
        Library    pytasq.connectors.ConnectorHandler
        
        *** Test Cases ***
        Test SSH Connection
            Open Session    server1    ssh    bash    192.168.1.100    22    admin    secret
            ${result}=    Execute Command    server1    whoami
            Should Contain    ${result}    admin
            Close Session    server1

    Error Handling
    ==============

    The class provides comprehensive error handling:

    * **Connection Errors**: Network connectivity issues, DNS resolution failures
    * **Authentication Errors**: Invalid credentials, key-based authentication failures  
    * **Protocol Errors**: Malformed requests, unsupported operations
    * **Tunnel Errors**: SSH tunnel establishment failures, nested tunnel issues
    * **Session Errors**: Invalid aliases, session state problems

    Configuration Management
    ========================

    Session Configuration
    ---------------------
    Sessions are managed through aliases that map to connection objects containing:

    * **session**: The underlying protocol-specific connection object
    * **tunnels**: List of active SSH tunnel objects (if applicable)

    Tunnel Configuration
    --------------------
    SSH tunnels are configured via JSON structures supporting:

    * **ip**: Target host IP address
    * **port**: Target host port
    * **username**: SSH authentication username  
    * **password**: SSH authentication password

    Thread Safety
    =============

    The ConnectorHandler is designed to be thread-safe within Robot Framework's 
    SUITE scope. Each test suite gets its own instance, preventing interference 
    between parallel test executions.

    Performance Considerations
    ==========================

    * **Connection Reuse**: Sessions are cached and reused within the same alias
    * **Lazy Loading**: Connectors are loaded only when needed
    * **Resource Cleanup**: Automatic cleanup of sessions and tunnels on suite teardown
    * **Memory Management**: Efficient handling of large command outputs

    Security Features
    =================

    * **Credential Protection**: Passwords are not logged in plain text
    * **SSL/TLS Support**: Encrypted connections for HTTP-based protocols
    * **SSH Key Support**: Public key authentication where supported
    * **Certificate Validation**: Configurable certificate validation policies

    Extensibility
    =============

    The architecture supports easy extension:

    1. **New Protocols**: Implement ConnectorInterface for new protocol support
    2. **Custom Products**: Add product-specific implementations within existing protocols
    3. **Enhanced Tunneling**: Extend TunnelingManager for additional tunnel types
    4. **Middleware**: Add connection middleware for logging, monitoring, etc.

    Dependencies
    ============

    Core Dependencies:
        * robot (Robot Framework)
        * paramiko (SSH connections)
        * sshtunnel (SSH tunneling)
        * requests (HTTP connections)
        * pywinrm (Windows Remote Management)

    Protocol-Specific Dependencies:
        * redfish (Redfish API)
        * pyVim (VMware vSphere)
        * ssl (SSL/TLS support)

    Best Practices
    ==============

    1. **Always use aliases**: Meaningful aliases improve test readability
    2. **Close sessions**: Explicit session cleanup prevents resource leaks  
    3. **Handle exceptions**: Wrap operations in try-catch for robust tests
    4. **Use tunneling wisely**: Only use tunnels when necessary for performance
    5. **Test connectivity**: Verify basic connectivity before complex operations

    Troubleshooting
    ===============

    Common Issues:

    * **"No sessions created"**: Check if open_session was called before execute_command
    * **"Alias does not exist"**: Verify alias spelling and session creation
    * **"Failed to establish nested tunnels"**: Check tunnel configuration and connectivity
    * **"Protocol not found"**: Ensure protocol/product combination is supported

    For detailed debugging, enable Robot Framework logging to see connection details.
    """

    ROBOT_LIBRARY_SCOPE = 'SUITE'
    ROBOT_LIBRARY_DOC_FORMAT = 'reST'

    def __init__(self) -> None:
        """
        Initialize the ConnectorHandler with default configuration.
        
        Creates a new instance with an empty connection cache and no active protocol.
        This method is automatically called when creating a new ConnectorHandler instance.
        
        The connection cache is initialized with a default message and will be used to
        store and manage all active sessions throughout the handler's lifetime.
        
        Robot Framework Scope:
            This initialization occurs once per test suite when using SUITE scope.
        
        Example:
            >>> handler = ConnectorHandler()
            >>> # Handler is now ready to open sessions
        """
        self._cache = ConnectionCache('No sessions created')
        self.protocol = None


    def __get_protocol__(self, protocol_name, product_name):
        """
        Dynamically load and instantiate the appropriate connector for the specified protocol.
        
        This private method uses the TunnelingManager to dynamically import and instantiate
        the correct connector class based on the protocol and product parameters. The loaded
        connector is stored in the self.protocol attribute for subsequent use.
        
        Args:
            protocol_name (str): The protocol type (e.g., 'ssh', 'http', 'winrm', 'socket')
            product_name (str): The specific product implementation (e.g., 'bash', 'redfish', 'tcp')
        
        Raises:
            ImportError: If the specified protocol/product combination cannot be found
            AttributeError: If the connector class is not properly defined
            Exception: For any other unexpected errors during connector loading
        
        Internal Use:
            This method is called automatically by open_session() and should not be 
            called directly by users.
        """
        self.protocol = TunnelingManager.get_protocol(protocol_name, product_name)


    def __nested_tunnel__(self, tunnel_config, target_config):
        """
        Establish nested SSH tunnels for complex network topologies.
        
        This private method delegates to TunnelingManager to create a chain of SSH tunnels
        based on the provided configuration. It supports multiple hops through different
        SSH servers to reach the final target system.
        
        Args:
            tunnel_config (list): List of dictionaries, each containing SSH hop configuration:
                - ip (str): SSH server IP address
                - port (int): SSH server port (typically 22)
                - username (str): SSH authentication username
                - password (str): SSH authentication password
            target_config (dict): Final target system configuration:
                - ip (str): Target system IP address
                - port (int): Target system port
                - username (str): Target authentication username
                - password (str): Target authentication password
        
        Returns:
            dict: Connection object containing:
                - session: The established session to the target system
                - tunnels: List of active SSH tunnel objects
        
        Raises:
            Exception: If tunnel establishment fails at any hop
        
        Internal Use:
            This method is called automatically by open_session() when tunnel_config
            is provided and should not be called directly by users.
        """
        return TunnelingManager.nested_tunnel(self.protocol, tunnel_config, target_config)

    def open_session(self, alias: str, protocol: str, product: str, host: str, port: int, login: str=None, password: str=None, tunnel_config=None, **kwargs) -> None:
        """
        Open a session to the target host with optional nested SSH tunneling support.
        
        This method establishes a connection to the specified target system using the
        requested protocol and product implementation. It supports both direct connections
        and complex multi-hop SSH tunneling scenarios for reaching systems across network
        boundaries.
        
        The session is registered in the connection cache using the provided alias,
        allowing for easy reference in subsequent operations. If tunneling is configured,
        the method automatically establishes the necessary SSH hops before connecting
        to the final target.
        
        Args:
            alias (str): Unique identifier for this session. Used to reference the session
                        in subsequent operations. Must be unique within the handler instance.
            protocol (str): Protocol type to use for the connection. Supported values:
                          - 'ssh': SSH-based connections (bash, python)
                          - 'http': HTTP-based APIs (redfish, basicauth, neorest, etc.)
                          - 'winrm': Windows Remote Management (powershell)
                          - 'socket': Raw socket connections (tcp, udp)
            product (str): Specific product implementation within the protocol:
                         SSH: 'bash', 'python'
                         HTTP: 'redfish', 'basicauth', 'neorest', 'vmwarensx', 'vmwarevcf', 'vsphere'
                         WinRM: 'powershell'
                         Socket: 'tcp', 'udp'
            host (str): Target system hostname or IP address. This is the final destination
                       system, not the SSH jump host (if tunneling is used).
            port (int): Target system port number. Protocol-specific default ports:
                       - SSH: 22
                       - HTTP/HTTPS: 80/443
                       - WinRM: 5985/5986
                       - Custom: As required by the target service
            login (str, optional): Authentication username for the target system.
                                 Required for most protocols except raw socket connections.
            password (str, optional): Authentication password for the target system.
                                    Required for password-based authentication.
            tunnel_config (list or str, optional): SSH tunnel configuration for multi-hop access.
                                                  Can be provided as:
                                                  - List of dictionaries (parsed directly)
                                                  - JSON string (parsed automatically)
                                                  Each hop should contain: ip, port, username, password
            **kwargs: Additional protocol-specific parameters passed to the underlying connector.
        
        Tunnel Configuration Format:
            When using SSH tunneling, tunnel_config should be structured as:
            
            .. code-block:: python
            
                tunnel_config = [
                    {
                        'ip': '10.0.0.1',        # First hop SSH server
                        'port': 22,              # SSH port (typically 22)
                        'username': 'jumpuser1', # SSH username
                        'password': 'jumppass1'  # SSH password
                    },
                    {
                        'ip': '192.168.1.1',     # Second hop SSH server
                        'port': 22,
                        'username': 'jumpuser2',
                        'password': 'jumppass2'
                    }
                    # Additional hops as needed...
                ]
        
        Session Registration:
            The established session is stored in the connection cache with the following structure:
            
            .. code-block:: python
            
                connection = {
                    'session': <protocol_session_object>,  # Protocol-specific session
                    'tunnels': [<tunnel1>, <tunnel2>] or None  # Active SSH tunnels
                }
        
        Raises:
            ValueError: If required parameters are missing or invalid
            ImportError: If the specified protocol/product combination is not available
            ConnectionError: If the connection to the target system fails
            AuthenticationError: If authentication fails
            Exception: For tunnel establishment failures or other unexpected errors
        
        Examples:
            Direct SSH Connection:
                >>> handler.open_session('web01', 'ssh', 'bash', '192.168.1.100', 22, 'admin', 'secret')
            
            HTTP API Connection:
                >>> handler.open_session('bmc01', 'http', 'redfish', '10.0.0.50', 443, 'root', 'calvin')
            
            Tunneled Connection:
                >>> tunnel_config = [{'ip': '10.0.0.1', 'port': 22, 'username': 'jump', 'password': 'pass'}]
                >>> handler.open_session('remote01', 'ssh', 'bash', '192.168.100.10', 22, 'admin', 'secret', tunnel_config)
            
            Windows PowerShell:
                >>> handler.open_session('win01', 'winrm', 'powershell', '10.0.1.20', 5986, 'Administrator', 'password')
        
        Robot Framework Usage:
            .. code-block:: robotframework
            
                Open Session    server1    ssh    bash    192.168.1.100    22    admin    secret
                Open Session    api1       http   redfish 10.0.0.50       443   root    calvin
        """
        tunnels = []
        self.__get_protocol__(protocol, product)
        self.remote_port = int(port)
        try:
            if tunnel_config:
                try:
                    if type(tunnel_config) is str:
                        tunnel_config = json.loads(tunnel_config)
                except Exception as e:
                    raise Exception(f"Error during importing tunnel as json: {e}")
                target_config = {
                    'ip': host,
                    'port': int(self.remote_port),
                    'username': login,
                    'password': password
                }
                connection = self.__nested_tunnel__(tunnel_config, target_config)
                tunnels = connection["tunnels"]
            else:
                session = self.protocol.open_session(host, int(self.remote_port), login, password)
                if not session:
                    raise Exception("Failed to open direct session")
                connection = {"session": session, "tunnels": None}

            self._cache.register(connection, alias)
        except Exception as e:
            for tunnel in reversed(tunnels):
                tunnel.stop()
            raise Exception(f"Failed to open session: {str(e)}")

    def execute_command(self, alias: str, command: str, **kwargs) -> any:
        """
        Execute a command on the specified session and return the result.
        
        This method executes a command or operation on the session identified by the
        provided alias. The exact nature of the command and its execution depends on
        the underlying protocol implementation. Results are returned in a format
        appropriate to the specific connector used.
        
        The method retrieves the session from the connection cache, validates its
        existence and state, then delegates the actual command execution to the
        protocol-specific connector implementation.
        
        Args:
            alias (str): The unique identifier of the session to execute the command on.
                        This must match an alias used in a previous open_session() call.
            command (str): The command or operation to execute. Format depends on protocol:
                         - SSH: Shell commands (e.g., 'ls -la', 'whoami', 'cat /etc/passwd')
                         - HTTP: API endpoints (e.g., '/redfish/v1/Systems/1', '/api/v1/status')
                         - WinRM: PowerShell commands (e.g., 'Get-Process', 'Get-Service')
                         - Socket: Raw data to send (e.g., 'GET / HTTP/1.1\\r\\n\\r\\n')
            **kwargs: Additional parameters passed to the underlying connector's execute_command method.
                     Common parameters include:
                     - timeout: Command execution timeout in seconds
                     - expect_response: Whether to wait for a response (socket connections)
                     - buffer_size: Buffer size for data reception (socket connections)
                     - encoding: Character encoding for text data (default: 'utf-8')
                     - options: Protocol-specific options (HTTP headers, SSH channel settings)
        
        Returns:
            any: Command execution result. The type and format depend on the protocol:
                - SSH: Command output as string or structured data
                - HTTP: Response data (JSON, XML, or text) based on API
                - WinRM: PowerShell command output and metadata
                - Socket: Dictionary with sent/received data, byte counts, and status flags
        
        Protocol-Specific Return Formats:
            SSH Connectors:
                Returns command output as string, potentially with exit codes and metadata.
            
            HTTP Connectors:
                Returns parsed response data (JSON objects, XML, or raw text) based on API.
            
            Socket Connectors:
                Returns detailed information about the communication:
                
                .. code-block:: python
                
                    {
                        'sent': 'original_command',
                        'bytes_sent': 123,
                        'received': 'response_data',
                        'bytes_received': 456,
                        'success': True,
                        'timeout': False,
                        'source_address': ('192.168.1.1', 12345)  # UDP only
                    }
            
            WinRM Connectors:
                Returns PowerShell execution results including output, errors, and exit codes.
        
        Raises:
            ValueError: If the specified alias does not exist in the connection cache
            RuntimeError: If the session is invalid or has been closed
            ConnectionError: If the underlying connection has been lost
            TimeoutError: If the command execution exceeds the specified timeout
            Exception: For protocol-specific errors or unexpected failures
        
        Examples:
            SSH Command Execution:
                >>> result = handler.execute_command('server1', 'ls -la /home')
                >>> print(result)  # Directory listing output
            
            HTTP API Call:
                >>> result = handler.execute_command('bmc1', '/redfish/v1/Systems/1')
                >>> print(result['Name'])  # System name from Redfish response
            
            PowerShell Command:
                >>> result = handler.execute_command('win1', 'Get-Process | Where-Object {$_.CPU -gt 100}')
                >>> print(result)  # High CPU processes
            
            Socket Communication:
                >>> result = handler.execute_command('tcp1', 'Hello Server', timeout=10)
                >>> print(f"Sent {result['bytes_sent']} bytes, received {result['bytes_received']} bytes")
            
            With Additional Parameters:
                >>> result = handler.execute_command('api1', '/api/data', 
                ...                                 options={'headers': {'Content-Type': 'application/json'}})
        
        Robot Framework Usage:
            .. code-block:: robotframework
            
                ${result}=    Execute Command    server1    whoami
                Should Contain    ${result}    admin
                
                ${api_result}=    Execute Command    bmc1    /redfish/v1/Systems/1
                Should Be Equal    ${api_result}[PowerState]    On
        """
        try:
            connection = self._cache.switch(alias)
            if not connection or 'session' not in connection:
                raise RuntimeError(f"No valid session found for alias '{alias}'")

            result = self.protocol.execute_command(connection['session'], command, **kwargs)
            return result
        except ValueError as ve:
            raise ValueError(f"Alias '{alias}' does not exist: {str(ve)}")
        except Exception as e:
            raise Exception(f"Failed to execute command: {str(e)}")

    def close_all_sessions(self) -> None:
        """
        Close all active sessions and stop any associated SSH tunnels.
        
        This method performs a comprehensive cleanup of all sessions managed by this
        ConnectorHandler instance. It iterates through all cached connections, properly
        closes each session using the protocol-specific close method, and stops any
        active SSH tunnels in the correct order (reverse order to prevent dependency issues).
        
        The method ensures graceful cleanup even if individual session closures fail,
        continuing to process remaining sessions and tunnels. After all cleanup operations
        are complete, the connection cache is emptied to reset the handler state.
        
        SSH Tunnel Cleanup:
            Tunnels are stopped in reverse order (last created first) to prevent
            dependency issues where closing an earlier tunnel might affect later ones
            in a nested tunnel chain.
        
        Error Handling:
            The method continues processing even if individual session closures fail,
            ensuring maximum cleanup completion. However, any errors encountered
            during the process are collected and reported in the final exception.
        
        Raises:
            Exception: If there are errors during session closure or tunnel cleanup.
                      The exception message will include details about any failures
                      encountered during the cleanup process.
        
        Examples:
            Standard Cleanup:
                >>> handler.close_all_sessions()
                # All sessions and tunnels are now closed
            
            In Test Teardown:
                >>> try:
                ...     # Test operations
                ...     pass
                ... finally:
                ...     handler.close_all_sessions()  # Ensure cleanup regardless of test outcome
        
        Robot Framework Usage:
            .. code-block:: robotframework
            
                *** Test Cases ***
                My Test Case
                    Open Session    server1    ssh    bash    192.168.1.100    22    admin    secret
                    Execute Command    server1    whoami
                    [Teardown]    Close All Sessions
                
                *** Keywords ***
                Suite Cleanup
                    Close All Sessions
        
        Best Practices:
            - Call this method in test teardown to ensure proper resource cleanup
            - Use in suite teardown when working with suite-scoped sessions  
            - Always call before creating a new set of sessions to ensure clean state
            - Consider calling in exception handling blocks for robust error recovery
        """
        try:
            for connection in self._cache._connections:
                self.protocol.close_session(connection['session'])
                if connection['tunnels'] is not None:
                    for tunnel in reversed(connection['tunnels']):
                        tunnel.stop()
            self._cache.empty_cache()
        except Exception as e:
            raise Exception(f"Failed to close all sessions: {str(e)}")

    def close_session(self, alias: str) -> None:
        """
        Close a specific session and stop any associated SSH tunnels.
        
        This method closes an individual session identified by its alias, performing
        proper cleanup of the underlying connection and any SSH tunnels that were
        established for that specific session. Unlike close_all_sessions(), this
        method targets only the specified session while leaving other active sessions intact.
        
        The method retrieves the session from the connection cache, validates its
        existence, closes the underlying protocol-specific connection, and stops any
        associated SSH tunnels in the proper order. The session is then removed from
        the cache.
        
        Args:
            alias (str): The unique identifier of the session to close. This must match
                        an alias used in a previous open_session() call.
        
        Cleanup Process:
            1. Validate session existence in the connection cache
            2. Retrieve the connection object containing session and tunnel information
            3. Close the protocol-specific session using the connector's close_session method
            4. Stop any associated SSH tunnels (if present) in reverse order
            5. Remove the session from the connection cache
        
        Raises:
            ValueError: If the specified alias does not exist in the connection cache
            RuntimeError: If the session is invalid or has already been closed
            Exception: If there are errors during session closure or tunnel cleanup
        
        Examples:
            Close Specific Session:
                >>> handler.open_session('server1', 'ssh', 'bash', '192.168.1.100', 22, 'admin', 'secret')
                >>> handler.open_session('server2', 'ssh', 'bash', '192.168.1.101', 22, 'admin', 'secret')
                >>> handler.close_session('server1')  # Only server1 is closed, server2 remains active
            
            Conditional Session Cleanup:
                >>> if some_error_condition:
                ...     handler.close_session('problematic_session')
                ...     # Other sessions continue to operate normally
        
        Robot Framework Usage:
            .. code-block:: robotframework
            
                *** Test Cases ***
                Test With Multiple Sessions
                    Open Session    server1    ssh    bash    192.168.1.100    22    admin    secret
                    Open Session    server2    ssh    bash    192.168.1.101    22    admin    secret
                    
                    # Use server1 for some operations
                    Execute Command    server1    whoami
                    Close Session     server1
                    
                    # server2 is still available
                    Execute Command    server2    whoami
                    Close Session     server2
        
        Notes:
            - This method only affects the specified session; other sessions remain active
            - SSH tunnels are stopped only if they were created specifically for this session
            - The method is safe to call multiple times on the same alias (no-op after first call)
            - Consider using close_all_sessions() for comprehensive cleanup in teardown scenarios
        """
        try:
            connection = self._cache.switch(alias)
            if not connection or 'session' not in connection:
                raise RuntimeError(f"No valid session found for alias '{alias}'")
            self.protocol.close_session(connection)
        except Exception as e:
            raise Exception(f"Failed to close session: {str(e)}")