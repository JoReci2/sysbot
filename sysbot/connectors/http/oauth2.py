import requests
from requests_oauthlib import OAuth2Session
from sysbot.utils.engine import ConnectorInterface


class Oauth2(ConnectorInterface):
    """
    HTTP/HTTPS connector with OAuth 2.0 authentication.
    """

    def open_session(self, host, port, login=None, password=None, **kwargs):
        """
        Opens an HTTP/HTTPS session with OAuth 2.0 authentication.
        
        Args:
            host (str): Hostname or IP address
            port (int): Port number
            login (str): OAuth client ID
            password (str): OAuth client secret
            **kwargs: Additional parameters:
                - protocol: 'http' or 'https' (default: 'https')
                - verify_ssl: Verify SSL certificates (default: False)
                - oauth_client_id: OAuth 2.0 client ID (alternative to login)
                - oauth_client_secret: OAuth 2.0 client secret (alternative to password)
                - oauth_token_url: OAuth 2.0 token URL
                - access_token: Pre-obtained access token
                
        Returns:
            dict: Session data containing connection parameters
        """
        protocol = kwargs.get('protocol', 'https')
        verify_ssl = kwargs.get('verify_ssl', False)
        oauth_client_id = kwargs.get('oauth_client_id', login)
        oauth_client_secret = kwargs.get('oauth_client_secret', password)
        oauth_token_url = kwargs.get('oauth_token_url')
        access_token = kwargs.get('access_token')
        
        session_data = {
            'host': host,
            'port': port,
            'protocol': protocol,
            'verify_ssl': verify_ssl,
            'oauth_client_id': oauth_client_id,
            'oauth_client_secret': oauth_client_secret,
            'oauth_token_url': oauth_token_url,
            'access_token': access_token,
        }
        
        # Create OAuth2Session if client_id is provided
        if oauth_client_id and oauth_token_url:
            oauth_session = OAuth2Session(oauth_client_id)
            session_data['oauth_session'] = oauth_session
        
        return session_data

    def execute_command(self, session, command, options=None):
        """
        Executes an HTTP request with OAuth 2.0 authentication.
        
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
            # Use OAuth2Session if available
            oauth_session = session.get('oauth_session')
            if oauth_session:
                response = oauth_session.request(
                    method,
                    base_url,
                    **request_kwargs
                )
            else:
                # Use access token if available
                access_token = session.get('access_token')
                if access_token:
                    headers['Authorization'] = f"Bearer {access_token}"
                    request_kwargs['headers'] = headers
                
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
        # Close OAuth2 session if exists
        oauth_session = session.get('oauth_session')
        if oauth_session:
            oauth_session.close()
