import requests
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth1, OAuth2Session
import jwt as jwt_lib
import hmac
import hashlib
import base64
from datetime import datetime, timedelta
from sysbot.utils.engine import ConnectorInterface


class Http(ConnectorInterface):
    """
    Generic HTTP/HTTPS connector supporting multiple authentication methods.
    
    Supported authentication methods:
    - none: No authentication
    - apikey: API Key authentication (header or query parameter)
    - basic: HTTP Basic Authentication
    - bearer: Bearer token (JWT or other)
    - oauth1: OAuth 1.0
    - oauth2: OAuth 2.0
    - jwt: JWT token generation and authentication
    - hmac: HMAC signature authentication
    - certificate: Client certificate authentication
    - openid: OpenID Connect
    - saml: SAML authentication (placeholder for external SAML flow)
    """

    def open_session(self, host, port, login=None, password=None, **kwargs):
        """
        Opens an HTTP/HTTPS session.
        
        Args:
            host (str): Hostname or IP address
            port (int): Port number
            login (str): Username or API key (optional, depends on auth method)
            password (str): Password or secret (optional, depends on auth method)
            **kwargs: Additional authentication parameters:
                - protocol: 'http' or 'https' (default: 'https')
                - auth_method: Authentication method (default: 'none')
                - verify_ssl: Verify SSL certificates (default: False)
                - cert_path: Path to client certificate file (for certificate auth)
                - key_path: Path to client key file (for certificate auth)
                - token: Bearer token or JWT token
                - api_key_name: Name of API key header/parameter (for apikey auth)
                - api_key_location: 'header' or 'query' (for apikey auth, default: 'header')
                - oauth_consumer_key: OAuth 1.0 consumer key
                - oauth_consumer_secret: OAuth 1.0 consumer secret
                - oauth_token_url: OAuth 2.0 token URL
                - oauth_authorize_url: OAuth 2.0 authorize URL
                - oauth_client_id: OAuth 2.0 client ID
                - oauth_client_secret: OAuth 2.0 client secret
                - jwt_secret: Secret for JWT signing
                - jwt_algorithm: Algorithm for JWT (default: 'HS256')
                - jwt_expiry: JWT expiration time in seconds (default: 3600)
                - hmac_secret: Secret for HMAC signature
                - hmac_algorithm: HMAC algorithm (default: 'sha256')
                - openid_discovery_url: OpenID Connect discovery URL
                - saml_assertion: SAML assertion token
                
        Returns:
            dict: Session data containing connection parameters
        """
        protocol = kwargs.get('protocol', 'https')
        auth_method = kwargs.get('auth_method', 'none')
        verify_ssl = kwargs.get('verify_ssl', False)
        
        session_data = {
            'host': host,
            'port': port,
            'protocol': protocol,
            'auth_method': auth_method,
            'verify_ssl': verify_ssl,
            'login': login,
            'password': password,
        }
        
        # Store all additional kwargs for authentication
        for key, value in kwargs.items():
            if key not in ['protocol', 'auth_method', 'verify_ssl']:
                session_data[key] = value
        
        # For certificate authentication, prepare the cert tuple
        if auth_method == 'certificate':
            cert_path = kwargs.get('cert_path')
            key_path = kwargs.get('key_path')
            if cert_path:
                session_data['cert'] = (cert_path, key_path) if key_path else cert_path
        
        # For OAuth2, create session
        if auth_method == 'oauth2':
            client_id = kwargs.get('oauth_client_id')
            token_url = kwargs.get('oauth_token_url')
            if client_id and token_url:
                oauth_session = OAuth2Session(client_id)
                session_data['oauth_session'] = oauth_session
        
        return session_data

    def execute_command(self, session, command, options=None):
        """
        Executes an HTTP request.
        
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
        
        # Prepare authentication
        auth = None
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
        
        auth_method = session['auth_method']
        
        try:
            # Apply authentication based on method
            if auth_method == 'none':
                pass  # No authentication
                
            elif auth_method == 'basic':
                auth = HTTPBasicAuth(session['login'], session['password'])
                request_kwargs['auth'] = auth
                
            elif auth_method == 'bearer' or auth_method == 'jwt':
                token = session.get('token')
                if not token and auth_method == 'jwt':
                    # Generate JWT token
                    token = self._generate_jwt(session)
                if token:
                    headers['Authorization'] = f'Bearer {token}'
                    request_kwargs['headers'] = headers
                    
            elif auth_method == 'apikey':
                api_key = session.get('login') or session.get('api_key')
                api_key_name = session.get('api_key_name', 'X-API-Key')
                api_key_location = session.get('api_key_location', 'header')
                
                if api_key_location == 'header':
                    headers[api_key_name] = api_key
                    request_kwargs['headers'] = headers
                else:  # query
                    params[api_key_name] = api_key
                    request_kwargs['params'] = params
                    
            elif auth_method == 'oauth1':
                oauth_consumer_key = session.get('oauth_consumer_key') or session.get('login')
                oauth_consumer_secret = session.get('oauth_consumer_secret') or session.get('password')
                oauth_token = session.get('oauth_token')
                oauth_token_secret = session.get('oauth_token_secret')
                
                auth = OAuth1(
                    oauth_consumer_key,
                    client_secret=oauth_consumer_secret,
                    resource_owner_key=oauth_token,
                    resource_owner_secret=oauth_token_secret
                )
                request_kwargs['auth'] = auth
                
            elif auth_method == 'oauth2':
                oauth_session = session.get('oauth_session')
                if oauth_session:
                    # Use OAuth2Session to make request
                    response = oauth_session.request(
                        method,
                        base_url,
                        **request_kwargs
                    )
                    return response
                else:
                    # Try using access token if available
                    access_token = session.get('access_token') or session.get('token')
                    if access_token:
                        headers['Authorization'] = f'Bearer {access_token}'
                        request_kwargs['headers'] = headers
                        
            elif auth_method == 'hmac':
                # Add HMAC signature to headers
                signature = self._generate_hmac_signature(
                    session,
                    method,
                    command,
                    params,
                    data or json_data
                )
                headers['X-HMAC-Signature'] = signature
                request_kwargs['headers'] = headers
                
            elif auth_method == 'certificate':
                cert = session.get('cert')
                if cert:
                    request_kwargs['cert'] = cert
                    
            elif auth_method == 'openid':
                # OpenID Connect uses bearer token
                access_token = session.get('access_token') or session.get('token')
                if access_token:
                    headers['Authorization'] = f'Bearer {access_token}'
                    request_kwargs['headers'] = headers
                    
            elif auth_method == 'saml':
                # SAML typically uses assertion in header or POST body
                saml_assertion = session.get('saml_assertion')
                if saml_assertion:
                    headers['SAML-Assertion'] = saml_assertion
                    request_kwargs['headers'] = headers
            
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
        try:
            # Close OAuth2 session if exists
            if 'oauth_session' in session:
                oauth_session = session.pop('oauth_session', None)
                if oauth_session:
                    oauth_session.close()
        except Exception as e:
            raise Exception(f"Failed to close HTTP session: {str(e)}")

    def _generate_jwt(self, session):
        """
        Generate a JWT token.
        
        Args:
            session (dict): Session data containing JWT parameters
            
        Returns:
            str: Generated JWT token
        """
        from datetime import timezone
        
        jwt_secret = session.get('jwt_secret') or session.get('password')
        jwt_algorithm = session.get('jwt_algorithm', 'HS256')
        jwt_expiry = session.get('jwt_expiry', 3600)
        
        if not jwt_secret:
            raise ValueError("JWT secret is required for JWT authentication")
        
        payload = {
            'sub': session.get('login', 'user'),
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

    def _generate_hmac_signature(self, session, method, path, params, body):
        """
        Generate an HMAC signature for the request.
        
        Args:
            session (dict): Session data containing HMAC parameters
            method (str): HTTP method
            path (str): Request path
            params (dict): Query parameters
            body: Request body
            
        Returns:
            str: HMAC signature
        """
        hmac_secret = session.get('hmac_secret') or session.get('password')
        hmac_algorithm = session.get('hmac_algorithm', 'sha256')
        
        if not hmac_secret:
            raise ValueError("HMAC secret is required for HMAC authentication")
        
        # Validate algorithm against whitelist to prevent arbitrary attribute access
        allowed_algorithms = ['sha1', 'sha224', 'sha256', 'sha384', 'sha512']
        if hmac_algorithm not in allowed_algorithms:
            raise ValueError(f"HMAC algorithm must be one of {allowed_algorithms}")
        
        # Build string to sign
        string_to_sign = f"{method}\n{path}\n"
        
        if params:
            sorted_params = sorted(params.items())
            string_to_sign += '&'.join([f"{k}={v}" for k, v in sorted_params])
        
        if body:
            if isinstance(body, dict):
                body = str(body)
            elif isinstance(body, bytes):
                body = body.decode('utf-8')
            string_to_sign += f"\n{body}"
        
        # Generate signature
        algorithm = getattr(hashlib, hmac_algorithm)
        signature = hmac.new(
            hmac_secret.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            algorithm
        ).digest()
        
        return base64.b64encode(signature).decode('utf-8')
