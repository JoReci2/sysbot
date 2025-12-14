from sysbot.connectors.http.generic import Generic


class Basicauth(Generic):
    """
    This class provides methods for interacting with an API using basic authentication.
    It wraps the generic HTTP connector with basic auth defaults for backward compatibility.
    """

    def open_session(self, host, port, login, password, **kwargs):
        """
        Opens a session to an API with basic auth.
        
        Args:
            host (str): Hostname or IP address
            port (int): Port number
            login (str): Username for basic authentication
            password (str): Password for basic authentication
            **kwargs: Additional parameters (protocol, verify_ssl, etc.)
        """
        # Set default authentication method to basic
        kwargs['auth_method'] = 'basic'
        
        # Default to HTTPS if not specified
        if 'protocol' not in kwargs:
            kwargs['protocol'] = 'https'
        
        return super().open_session(host, port, login, password, **kwargs)

    def execute_command(self, session, command, options=None):
        """
        Executes a command on an API with basic auth.
        
        Args:
            session (dict): Session data
            command (str): URL path
            options (dict): Request options
            
        Returns:
            bytes: Response content (for backward compatibility)
        """
        # Ensure auth_method is set to basic
        session['auth_method'] = 'basic'
        
        # Call parent execute_command
        response = super().execute_command(session, command, options)
        
        # Check status code for backward compatibility
        if response.status_code != 200:
            raise Exception(f"HTTP status error: {response.status_code}")
        
        return response.content
