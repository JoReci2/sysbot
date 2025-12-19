import requests
from requests_oauthlib import OAuth1
from sysbot.utils.engine import ConnectorInterface


class Oauth1(ConnectorInterface):
    """
    HTTP/HTTPS connector with OAuth 1.0 authentication.
    """

    def open_session(self, host, port, login, password, **kwargs):
        """
        Opens an HTTP/HTTPS session with OAuth 1.0 authentication.
        
        Args:
            host (str): Hostname or IP address
            port (int): Port number
            login (str): OAuth consumer key
            password (str): OAuth consumer secret
            **kwargs: Additional parameters:
                - protocol: 'http' or 'https' (default: 'https')
                - verify_ssl: Verify SSL certificates (default: False)
                - oauth_token: OAuth access token
                - oauth_token_secret: OAuth token secret
                
        Returns:
            dict: Session data containing connection parameters
        """
        protocol = kwargs.get('protocol', 'https')
        verify_ssl = kwargs.get('verify_ssl', False)
        oauth_token = kwargs.get('oauth_token')
        oauth_token_secret = kwargs.get('oauth_token_secret')
        
        session_data = {
            'host': host,
            'port': port,
            'protocol': protocol,
            'verify_ssl': verify_ssl,
            'oauth_consumer_key': login,
            'oauth_consumer_secret': password,
            'oauth_token': oauth_token,
            'oauth_token_secret': oauth_token_secret,
        }
        
        return session_data

    def execute_command(self, session, command, options=None):
        """
        Executes an HTTP request with OAuth 1.0 authentication.
        
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
        
        # Create OAuth1 auth
        auth = OAuth1(
            session['oauth_consumer_key'],
            client_secret=session['oauth_consumer_secret'],
            resource_owner_key=session.get('oauth_token'),
            resource_owner_secret=session.get('oauth_token_secret')
        )
        
        # Prepare request kwargs
        request_kwargs = {
            'params': params,
            'headers': headers,
            'timeout': timeout,
            'verify': session['verify_ssl'],
            'auth': auth
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
