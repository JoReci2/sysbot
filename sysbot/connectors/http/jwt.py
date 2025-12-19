import requests
import jwt as jwt_lib
from datetime import datetime, timedelta, timezone
from sysbot.utils.engine import ConnectorInterface


class Jwt(ConnectorInterface):
    """
    HTTP/HTTPS connector with JWT token generation and authentication.
    """

    def open_session(self, host, port, login, password, **kwargs):
        """
        Opens an HTTP/HTTPS session with JWT authentication.
        
        Args:
            host (str): Hostname or IP address
            port (int): Port number
            login (str): Username/subject for JWT
            password (str): Secret key for JWT signing
            **kwargs: Additional parameters:
                - protocol: 'http' or 'https' (default: 'https')
                - verify_ssl: Verify SSL certificates (default: False)
                - jwt_algorithm: Algorithm for JWT (default: 'HS256')
                - jwt_expiry: JWT expiration time in seconds (default: 3600)
                - jwt_claims: Additional claims to include in JWT (dict)
                
        Returns:
            dict: Session data containing connection parameters
        """
        protocol = kwargs.get('protocol', 'https')
        verify_ssl = kwargs.get('verify_ssl', False)
        jwt_algorithm = kwargs.get('jwt_algorithm', 'HS256')
        jwt_expiry = kwargs.get('jwt_expiry', 3600)
        jwt_claims = kwargs.get('jwt_claims', {})
        
        session_data = {
            'host': host,
            'port': port,
            'protocol': protocol,
            'verify_ssl': verify_ssl,
            'login': login,
            'jwt_secret': password,
            'jwt_algorithm': jwt_algorithm,
            'jwt_expiry': jwt_expiry,
            'jwt_claims': jwt_claims,
        }
        
        return session_data

    def execute_command(self, session, command, options=None):
        """
        Executes an HTTP request with JWT authentication.
        
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
        
        # Generate JWT token
        token = self._generate_jwt(session)
        headers['Authorization'] = f"Bearer {token}"
        
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

    def _generate_jwt(self, session):
        """
        Generate a JWT token.
        
        Args:
            session (dict): Session data containing JWT parameters
            
        Returns:
            str: Generated JWT token
        """
        jwt_secret = session['jwt_secret']
        jwt_algorithm = session['jwt_algorithm']
        jwt_expiry = session['jwt_expiry']
        
        payload = {
            'sub': session['login'],
            'iat': datetime.now(timezone.utc),
            'exp': datetime.now(timezone.utc) + timedelta(seconds=jwt_expiry)
        }
        
        # Add any additional claims from session
        jwt_claims = session.get('jwt_claims', {})
        payload.update(jwt_claims)
        
        token = jwt_lib.encode(payload, jwt_secret, algorithm=jwt_algorithm)
        
        # Handle PyJWT version differences
        if isinstance(token, bytes):
            token = token.decode('utf-8')
        
        return token
