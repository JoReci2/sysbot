import requests
from sysbot.utils.engine import ConnectorInterface


class Apikey(ConnectorInterface):
    """
    HTTP/HTTPS connector with API Key authentication.
    """

    def open_session(self, host, port, login, password=None, **kwargs):
        """
        Opens an HTTP/HTTPS session with API Key authentication.
        
        Args:
            host (str): Hostname or IP address
            port (int): Port number
            login (str): API key
            password (str): Not used for this auth method
            **kwargs: Additional parameters:
                - protocol: 'http' or 'https' (default: 'https')
                - verify_ssl: Verify SSL certificates (default: False)
                - api_key_name: Name of API key header/parameter (default: 'X-API-Key')
                - api_key_location: 'header' or 'query' (default: 'header')
                
        Returns:
            dict: Session data containing connection parameters
        """
        protocol = kwargs.get('protocol', 'https')
        verify_ssl = kwargs.get('verify_ssl', False)
        api_key_name = kwargs.get('api_key_name', 'X-API-Key')
        api_key_location = kwargs.get('api_key_location', 'header')
        
        session_data = {
            'host': host,
            'port': port,
            'protocol': protocol,
            'verify_ssl': verify_ssl,
            'api_key': login,
            'api_key_name': api_key_name,
            'api_key_location': api_key_location,
        }
        
        return session_data

    def execute_command(self, session, command, options=None):
        """
        Executes an HTTP request with API Key authentication.
        
        Args:
            session (dict): Session data from open_session
            command (str): URL path (e.g., '/api/v1/resource')
            options (dict): Request options:
                - method: HTTP method (GET, POST, PUT, DELETE, PATCH, etc.) (default: 'GET')
                - params: Query parameters (dict)
                - data: Request body data (dict or str)
                - json: JSON request body (dict)
                - headers: Additional headers (dict)
                - timeout: Request timeout in seconds (default: 30)
                
        Returns:
            requests.Response: Response object
            
        Raises:
            Exception: If request fails
        """
        if options is None:
            options = {}
        
        # Build base URL
        base_url = f"{session['protocol']}://{session['host']}:{session['port']}{command}"
        
        # Get request parameters
        method = options.get('method', 'GET').upper()
        params = options.get('params', {})
        data = options.get('data')
        json_data = options.get('json')
        headers = options.get('headers', {})
        timeout = options.get('timeout', 30)
        
        # Add API key to headers or query parameters
        api_key = session['api_key']
        api_key_name = session['api_key_name']
        api_key_location = session['api_key_location']
        
        if api_key_location == 'header':
            headers[api_key_name] = api_key
        else:  # query
            params[api_key_name] = api_key
        
        # Prepare request kwargs
        request_kwargs = {
            'params': params,
            'headers': headers,
            'timeout': timeout,
            'verify': session['verify_ssl']
        }
        
        # Add body data if present
        if json_data is not None:
            request_kwargs['json'] = json_data
        elif data is not None:
            request_kwargs['data'] = data
        
        try:
            # Make the request
            response = requests.request(
                method,
                base_url,
                **request_kwargs
            )
            
            return response
            
        except Exception as e:
            raise Exception(f"Failed to execute HTTP request: {str(e)}")

    def close_session(self, session):
        """
        Closes the HTTP session.
        
        Args:
            session (dict): Session data
        """
        pass
