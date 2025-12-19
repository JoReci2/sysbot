import requests
import hmac
import hashlib
import base64
from sysbot.utils.engine import ConnectorInterface


class Hmac(ConnectorInterface):
    """
    HTTP/HTTPS connector with HMAC signature authentication.
    """

    def open_session(self, host, port, login=None, password=None, **kwargs):
        """
        Opens an HTTP/HTTPS session with HMAC authentication.
        
        Args:
            host (str): Hostname or IP address
            port (int): Port number
            login (str): Not used for this auth method
            password (str): HMAC secret key
            **kwargs: Additional parameters:
                - protocol: 'http' or 'https' (default: 'https')
                - verify_ssl: Verify SSL certificates (default: False)
                - hmac_secret: HMAC secret (alternative to password)
                - hmac_algorithm: HMAC algorithm (default: 'sha256')
                
        Returns:
            dict: Session data containing connection parameters
        """
        protocol = kwargs.get('protocol', 'https')
        verify_ssl = kwargs.get('verify_ssl', False)
        hmac_secret = kwargs.get('hmac_secret', password)
        hmac_algorithm = kwargs.get('hmac_algorithm', 'sha256')
        
        if not hmac_secret:
            raise ValueError("HMAC secret is required")
        
        # Validate algorithm against whitelist to prevent arbitrary attribute access
        allowed_algorithms = ['sha1', 'sha224', 'sha256', 'sha384', 'sha512']
        if hmac_algorithm not in allowed_algorithms:
            raise ValueError(f"HMAC algorithm must be one of {allowed_algorithms}")
        
        session_data = {
            'host': host,
            'port': port,
            'protocol': protocol,
            'verify_ssl': verify_ssl,
            'hmac_secret': hmac_secret,
            'hmac_algorithm': hmac_algorithm,
        }
        
        return session_data

    def execute_command(self, session, command, options=None):
        """
        Executes an HTTP request with HMAC signature authentication.
        
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
        
        # Generate HMAC signature
        signature = self._generate_hmac_signature(
            session,
            method,
            command,
            params,
            data or json_data
        )
        headers['X-HMAC-Signature'] = signature
        
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
        hmac_secret = session['hmac_secret']
        hmac_algorithm = session['hmac_algorithm']
        
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
