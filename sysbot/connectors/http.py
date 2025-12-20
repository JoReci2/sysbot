"""
HTTP/HTTPS Connector with Multiple Authentication Methods

This module provides a generic HTTP/HTTPS connector with support for various
authentication methods. Each authentication method is implemented as a separate
self-contained class.
"""

import requests
import hmac
import hashlib
import base64
import jwt as jwt_lib
from datetime import datetime, timedelta
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth1, OAuth2Session
from sysbot.utils.engine import ConnectorInterface


class BaseHttp(ConnectorInterface):
    """
    Base class for HTTP/HTTPS connectors providing common functionality.
    This class should not be used directly but extended by authentication-specific classes.
    """

    def __init__(self, port=443, use_https=True):
        """
        Initialize base HTTP connector.

        Args:
            port (int): Default port (default: 443 for HTTPS, 80 for HTTP).
            use_https (bool): Whether to use HTTPS (default: True).
        """
        super().__init__()
        self.default_port = port
        self.use_https = use_https

    def _build_url(self, host, port, endpoint):
        """
        Build the full URL for the request.

        Args:
            host (str): Hostname or IP address.
            port (int): Port number.
            endpoint (str): API endpoint path.

        Returns:
            str: The full URL.
        """
        protocol = "https" if self.use_https else "http"
        return f"{protocol}://{host}:{port}{endpoint}"

    def _make_request(self, method, url, auth=None, headers=None, params=None, data=None, json=None, verify=False):
        """
        Make an HTTP request with error handling.

        Args:
            method (str): HTTP method (GET, POST, PUT, DELETE, etc.).
            url (str): The URL to request.
            auth: Authentication object for requests library.
            headers (dict): HTTP headers.
            params (dict): URL parameters.
            data: Request body data.
            json: JSON request body.
            verify (bool): Whether to verify SSL certificates.

        Returns:
            requests.Response: The response object.

        Raises:
            Exception: If the request fails.
        """
        try:
            response = requests.request(
                method=method.upper(),
                url=url,
                auth=auth,
                headers=headers,
                params=params,
                data=data,
                json=json,
                verify=verify
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            raise Exception(f"HTTP request failed: {str(e)}")


class Apikey(BaseHttp):
    """
    HTTP connector with API Key authentication.
    Supports API keys in headers or query parameters.
    """

    def __init__(self, port=443, use_https=True):
        """
        Initialize API Key authentication connector.

        Args:
            port (int): Default port (default: 443).
            use_https (bool): Whether to use HTTPS (default: True).
        """
        super().__init__(port, use_https)

    def open_session(self, host, port=None, login=None, password=None, api_key=None, 
                     api_key_header="X-API-Key", api_key_in_query=False):
        """
        Opens a session with API key authentication.

        Args:
            host (str): Hostname or IP address.
            port (int): Port. If None, uses default_port.
            login (str): Not used for API key auth (for compatibility).
            password (str): Not used for API key auth (for compatibility).
            api_key (str): The API key.
            api_key_header (str): Header name for API key (default: "X-API-Key").
            api_key_in_query (bool): If True, send API key as query parameter instead of header.

        Returns:
            dict: Session configuration.
        """
        if port is None:
            port = self.default_port
        
        return {
            "host": host,
            "port": port,
            "api_key": api_key,
            "api_key_header": api_key_header,
            "api_key_in_query": api_key_in_query,
            "use_https": self.use_https
        }

    def execute_command(self, session, command, options=None):
        """
        Execute an HTTP request with API key authentication.

        Args:
            session (dict): Session configuration.
            command (str): API endpoint path.
            options (dict): Optional request parameters (method, params, headers, data, json).

        Returns:
            bytes: Response content.
        """
        url = self._build_url(session["host"], session["port"], command)
        
        method = options.get("method", "GET") if options else "GET"
        headers = options.get("headers", {}) if options else {}
        params = options.get("params", {}) if options else {}
        data = options.get("data") if options else None
        json_data = options.get("json") if options else None
        
        if session.get("api_key_in_query"):
            params[session["api_key_header"]] = session["api_key"]
        else:
            headers[session["api_key_header"]] = session["api_key"]
        
        response = self._make_request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            data=data,
            json=json_data
        )
        
        return response.content

    def close_session(self, session):
        """
        Close the session (no-op for API key auth).

        Args:
            session (dict): Session configuration.
        """
        pass


class Basicauth(BaseHttp):
    """
    HTTP connector with Basic Authentication (username/password).
    """

    def __init__(self, port=443, use_https=True):
        """
        Initialize Basic Auth connector.

        Args:
            port (int): Default port (default: 443).
            use_https (bool): Whether to use HTTPS (default: True).
        """
        super().__init__(port, use_https)

    def open_session(self, host, port=None, login=None, password=None):
        """
        Opens a session with Basic authentication.

        Args:
            host (str): Hostname or IP address.
            port (int): Port. If None, uses default_port.
            login (str): Username.
            password (str): Password.

        Returns:
            dict: Session configuration.
        """
        if port is None:
            port = self.default_port
        
        return {
            "host": host,
            "port": port,
            "login": login,
            "password": password,
            "use_https": self.use_https
        }

    def execute_command(self, session, command, options=None):
        """
        Execute an HTTP request with Basic authentication.

        Args:
            session (dict): Session configuration.
            command (str): API endpoint path.
            options (dict): Optional request parameters (method, params, headers, data, json).

        Returns:
            bytes: Response content.
        """
        url = self._build_url(session["host"], session["port"], command)
        
        method = options.get("method", "GET") if options else "GET"
        headers = options.get("headers") if options else None
        params = options.get("params") if options else None
        data = options.get("data") if options else None
        json_data = options.get("json") if options else None
        
        auth = HTTPBasicAuth(session["login"], session["password"])
        
        response = self._make_request(
            method=method,
            url=url,
            auth=auth,
            headers=headers,
            params=params,
            data=data,
            json=json_data
        )
        
        return response.content

    def close_session(self, session):
        """
        Close the session (no-op for Basic auth).

        Args:
            session (dict): Session configuration.
        """
        pass


class Oauth1(BaseHttp):
    """
    HTTP connector with OAuth 1.0 authentication.
    """

    def __init__(self, port=443, use_https=True):
        """
        Initialize OAuth 1.0 connector.

        Args:
            port (int): Default port (default: 443).
            use_https (bool): Whether to use HTTPS (default: True).
        """
        super().__init__(port, use_https)

    def open_session(self, host, port=None, login=None, password=None, 
                     client_key=None, client_secret=None, 
                     resource_owner_key=None, resource_owner_secret=None):
        """
        Opens a session with OAuth 1.0 authentication.

        Args:
            host (str): Hostname or IP address.
            port (int): Port. If None, uses default_port.
            login (str): Not used (for compatibility).
            password (str): Not used (for compatibility).
            client_key (str): OAuth consumer key.
            client_secret (str): OAuth consumer secret.
            resource_owner_key (str): OAuth token.
            resource_owner_secret (str): OAuth token secret.

        Returns:
            dict: Session configuration.
        """
        if port is None:
            port = self.default_port
        
        return {
            "host": host,
            "port": port,
            "client_key": client_key,
            "client_secret": client_secret,
            "resource_owner_key": resource_owner_key,
            "resource_owner_secret": resource_owner_secret,
            "use_https": self.use_https
        }

    def execute_command(self, session, command, options=None):
        """
        Execute an HTTP request with OAuth 1.0 authentication.

        Args:
            session (dict): Session configuration.
            command (str): API endpoint path.
            options (dict): Optional request parameters (method, params, headers, data, json).

        Returns:
            bytes: Response content.
        """
        url = self._build_url(session["host"], session["port"], command)
        
        method = options.get("method", "GET") if options else "GET"
        headers = options.get("headers") if options else None
        params = options.get("params") if options else None
        data = options.get("data") if options else None
        json_data = options.get("json") if options else None
        
        auth = OAuth1(
            session["client_key"],
            session["client_secret"],
            session["resource_owner_key"],
            session["resource_owner_secret"]
        )
        
        response = self._make_request(
            method=method,
            url=url,
            auth=auth,
            headers=headers,
            params=params,
            data=data,
            json=json_data
        )
        
        return response.content

    def close_session(self, session):
        """
        Close the session (no-op for OAuth 1.0).

        Args:
            session (dict): Session configuration.
        """
        pass


class Oauth2(BaseHttp):
    """
    HTTP connector with OAuth 2.0 authentication.
    """

    def __init__(self, port=443, use_https=True):
        """
        Initialize OAuth 2.0 connector.

        Args:
            port (int): Default port (default: 443).
            use_https (bool): Whether to use HTTPS (default: True).
        """
        super().__init__(port, use_https)

    def open_session(self, host, port=None, login=None, password=None,
                     client_id=None, client_secret=None, token_url=None,
                     access_token=None, refresh_token=None):
        """
        Opens a session with OAuth 2.0 authentication.

        Args:
            host (str): Hostname or IP address.
            port (int): Port. If None, uses default_port.
            login (str): Not used (for compatibility).
            password (str): Not used (for compatibility).
            client_id (str): OAuth 2.0 client ID.
            client_secret (str): OAuth 2.0 client secret.
            token_url (str): URL to obtain tokens.
            access_token (str): Existing access token (optional).
            refresh_token (str): Refresh token (optional).

        Returns:
            dict: Session configuration.
        """
        if port is None:
            port = self.default_port
        
        session_data = {
            "host": host,
            "port": port,
            "client_id": client_id,
            "client_secret": client_secret,
            "token_url": token_url,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "use_https": self.use_https
        }
        
        # If access_token is not provided, try to get one
        if not access_token and token_url and client_id and client_secret:
            try:
                oauth = OAuth2Session(client_id)
                token = oauth.fetch_token(
                    token_url=token_url,
                    client_id=client_id,
                    client_secret=client_secret
                )
                session_data["access_token"] = token.get("access_token")
                session_data["refresh_token"] = token.get("refresh_token")
            except Exception as e:
                raise Exception(f"Failed to obtain OAuth 2.0 token: {str(e)}")
        
        return session_data

    def execute_command(self, session, command, options=None):
        """
        Execute an HTTP request with OAuth 2.0 authentication.

        Args:
            session (dict): Session configuration.
            command (str): API endpoint path.
            options (dict): Optional request parameters (method, params, headers, data, json).

        Returns:
            bytes: Response content.
        """
        url = self._build_url(session["host"], session["port"], command)
        
        method = options.get("method", "GET") if options else "GET"
        headers = options.get("headers", {}) if options else {}
        params = options.get("params") if options else None
        data = options.get("data") if options else None
        json_data = options.get("json") if options else None
        
        # Add Bearer token to headers
        headers["Authorization"] = f"Bearer {session['access_token']}"
        
        response = self._make_request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            data=data,
            json=json_data
        )
        
        return response.content

    def close_session(self, session):
        """
        Close the session (no-op for OAuth 2.0).

        Args:
            session (dict): Session configuration.
        """
        pass


class Jwt(BaseHttp):
    """
    HTTP connector with JWT (JSON Web Token) authentication.
    """

    def __init__(self, port=443, use_https=True):
        """
        Initialize JWT connector.

        Args:
            port (int): Default port (default: 443).
            use_https (bool): Whether to use HTTPS (default: True).
        """
        super().__init__(port, use_https)

    def open_session(self, host, port=None, login=None, password=None,
                     secret_key=None, algorithm="HS256", token=None,
                     payload=None, expiration_minutes=60):
        """
        Opens a session with JWT authentication.

        Args:
            host (str): Hostname or IP address.
            port (int): Port. If None, uses default_port.
            login (str): Username to include in JWT payload (optional).
            password (str): Not used (for compatibility).
            secret_key (str): Secret key for signing JWT.
            algorithm (str): JWT signing algorithm (default: HS256).
            token (str): Existing JWT token (optional).
            payload (dict): Custom JWT payload (optional).
            expiration_minutes (int): Token expiration time in minutes (default: 60).

        Returns:
            dict: Session configuration.
        """
        if port is None:
            port = self.default_port
        
        # Generate token if not provided
        if not token and secret_key:
            if payload is None:
                payload = {}
            
            if login:
                payload["sub"] = login
            
            payload["exp"] = datetime.utcnow() + timedelta(minutes=expiration_minutes)
            payload["iat"] = datetime.utcnow()
            
            token = jwt_lib.encode(payload, secret_key, algorithm=algorithm)
        
        return {
            "host": host,
            "port": port,
            "token": token,
            "secret_key": secret_key,
            "algorithm": algorithm,
            "use_https": self.use_https
        }

    def execute_command(self, session, command, options=None):
        """
        Execute an HTTP request with JWT authentication.

        Args:
            session (dict): Session configuration.
            command (str): API endpoint path.
            options (dict): Optional request parameters (method, params, headers, data, json).

        Returns:
            bytes: Response content.
        """
        url = self._build_url(session["host"], session["port"], command)
        
        method = options.get("method", "GET") if options else "GET"
        headers = options.get("headers", {}) if options else {}
        params = options.get("params") if options else None
        data = options.get("data") if options else None
        json_data = options.get("json") if options else None
        
        # Add JWT to headers
        headers["Authorization"] = f"Bearer {session['token']}"
        
        response = self._make_request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            data=data,
            json=json_data
        )
        
        return response.content

    def close_session(self, session):
        """
        Close the session (no-op for JWT).

        Args:
            session (dict): Session configuration.
        """
        pass


class Saml(BaseHttp):
    """
    HTTP connector with SAML authentication.
    Note: SAML authentication typically requires browser-based flow.
    This implementation supports using SAML assertions/tokens.
    """

    def __init__(self, port=443, use_https=True):
        """
        Initialize SAML connector.

        Args:
            port (int): Default port (default: 443).
            use_https (bool): Whether to use HTTPS (default: True).
        """
        super().__init__(port, use_https)

    def open_session(self, host, port=None, login=None, password=None,
                     saml_token=None, saml_header="X-SAML-Token"):
        """
        Opens a session with SAML authentication.

        Args:
            host (str): Hostname or IP address.
            port (int): Port. If None, uses default_port.
            login (str): Not used (for compatibility).
            password (str): Not used (for compatibility).
            saml_token (str): SAML assertion/token.
            saml_header (str): Header name for SAML token (default: X-SAML-Token).

        Returns:
            dict: Session configuration.
        """
        if port is None:
            port = self.default_port
        
        return {
            "host": host,
            "port": port,
            "saml_token": saml_token,
            "saml_header": saml_header,
            "use_https": self.use_https
        }

    def execute_command(self, session, command, options=None):
        """
        Execute an HTTP request with SAML authentication.

        Args:
            session (dict): Session configuration.
            command (str): API endpoint path.
            options (dict): Optional request parameters (method, params, headers, data, json).

        Returns:
            bytes: Response content.
        """
        url = self._build_url(session["host"], session["port"], command)
        
        method = options.get("method", "GET") if options else "GET"
        headers = options.get("headers", {}) if options else {}
        params = options.get("params") if options else None
        data = options.get("data") if options else None
        json_data = options.get("json") if options else None
        
        # Add SAML token to headers
        headers[session["saml_header"]] = session["saml_token"]
        
        response = self._make_request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            data=data,
            json=json_data
        )
        
        return response.content

    def close_session(self, session):
        """
        Close the session (no-op for SAML).

        Args:
            session (dict): Session configuration.
        """
        pass


class Hmac(BaseHttp):
    """
    HTTP connector with HMAC authentication.
    """

    def __init__(self, port=443, use_https=True):
        """
        Initialize HMAC connector.

        Args:
            port (int): Default port (default: 443).
            use_https (bool): Whether to use HTTPS (default: True).
        """
        super().__init__(port, use_https)

    def open_session(self, host, port=None, login=None, password=None,
                     secret_key=None, algorithm="sha256", 
                     signature_header="X-Signature", 
                     timestamp_header="X-Timestamp"):
        """
        Opens a session with HMAC authentication.

        Args:
            host (str): Hostname or IP address.
            port (int): Port. If None, uses default_port.
            login (str): Access key/client ID.
            password (str): Not used (for compatibility).
            secret_key (str): Secret key for HMAC signing.
            algorithm (str): Hash algorithm (sha256, sha1, sha512, etc.).
            signature_header (str): Header name for signature (default: X-Signature).
            timestamp_header (str): Header name for timestamp (default: X-Timestamp).

        Returns:
            dict: Session configuration.
        """
        if port is None:
            port = self.default_port
        
        return {
            "host": host,
            "port": port,
            "access_key": login,
            "secret_key": secret_key,
            "algorithm": algorithm,
            "signature_header": signature_header,
            "timestamp_header": timestamp_header,
            "use_https": self.use_https
        }

    def _generate_signature(self, method, path, timestamp, body=""):
        """
        Generate HMAC signature for the request.

        Args:
            method (str): HTTP method.
            path (str): Request path.
            timestamp (str): Request timestamp.
            body (str): Request body.

        Returns:
            str: Base64-encoded HMAC signature.
        """
        # Create string to sign
        string_to_sign = f"{method}\n{path}\n{timestamp}\n{body}"
        
        # Get hash function
        hash_func = getattr(hashlib, self.session_algorithm, hashlib.sha256)
        
        # Generate HMAC
        signature = hmac.new(
            self.session_secret_key.encode(),
            string_to_sign.encode(),
            hash_func
        ).digest()
        
        # Return base64-encoded signature
        return base64.b64encode(signature).decode()

    def execute_command(self, session, command, options=None):
        """
        Execute an HTTP request with HMAC authentication.

        Args:
            session (dict): Session configuration.
            command (str): API endpoint path.
            options (dict): Optional request parameters (method, params, headers, data, json).

        Returns:
            bytes: Response content.
        """
        url = self._build_url(session["host"], session["port"], command)
        
        method = options.get("method", "GET") if options else "GET"
        headers = options.get("headers", {}) if options else {}
        params = options.get("params") if options else None
        data = options.get("data") if options else None
        json_data = options.get("json") if options else None
        
        # Generate timestamp
        timestamp = str(int(datetime.utcnow().timestamp()))
        
        # Store session data for signature generation
        self.session_algorithm = session["algorithm"]
        self.session_secret_key = session["secret_key"]
        
        # Generate signature
        body = ""
        if data:
            body = str(data)
        elif json_data:
            import json
            body = json.dumps(json_data)
        
        signature = self._generate_signature(method, command, timestamp, body)
        
        # Add authentication headers
        if session.get("access_key"):
            headers["X-Access-Key"] = session["access_key"]
        headers[session["timestamp_header"]] = timestamp
        headers[session["signature_header"]] = signature
        
        response = self._make_request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            data=data,
            json=json_data
        )
        
        return response.content

    def close_session(self, session):
        """
        Close the session (no-op for HMAC).

        Args:
            session (dict): Session configuration.
        """
        pass


class Certificate(BaseHttp):
    """
    HTTP connector with Client Certificate authentication (mutual TLS).
    """

    def __init__(self, port=443, use_https=True):
        """
        Initialize Certificate connector.

        Args:
            port (int): Default port (default: 443).
            use_https (bool): Whether to use HTTPS (default: True).
        """
        super().__init__(port, use_https)

    def open_session(self, host, port=None, login=None, password=None,
                     cert_file=None, key_file=None, ca_bundle=None):
        """
        Opens a session with client certificate authentication.

        Args:
            host (str): Hostname or IP address.
            port (int): Port. If None, uses default_port.
            login (str): Not used (for compatibility).
            password (str): Password for encrypted key file (optional).
            cert_file (str): Path to client certificate file.
            key_file (str): Path to private key file (optional, can be in cert_file).
            ca_bundle (str): Path to CA bundle for server verification (optional).

        Returns:
            dict: Session configuration.
        """
        if port is None:
            port = self.default_port
        
        return {
            "host": host,
            "port": port,
            "cert_file": cert_file,
            "key_file": key_file,
            "ca_bundle": ca_bundle,
            "key_password": password,
            "use_https": self.use_https
        }

    def execute_command(self, session, command, options=None):
        """
        Execute an HTTP request with certificate authentication.

        Args:
            session (dict): Session configuration.
            command (str): API endpoint path.
            options (dict): Optional request parameters (method, params, headers, data, json).

        Returns:
            bytes: Response content.
        """
        url = self._build_url(session["host"], session["port"], command)
        
        method = options.get("method", "GET") if options else "GET"
        headers = options.get("headers") if options else None
        params = options.get("params") if options else None
        data = options.get("data") if options else None
        json_data = options.get("json") if options else None
        
        # Prepare certificate tuple
        if session.get("key_file"):
            cert = (session["cert_file"], session["key_file"])
        else:
            cert = session["cert_file"]
        
        # Determine verification setting
        verify = session.get("ca_bundle", False)
        
        try:
            response = requests.request(
                method=method.upper(),
                url=url,
                cert=cert,
                verify=verify,
                headers=headers,
                params=params,
                data=data,
                json=json_data
            )
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            raise Exception(f"HTTP request with certificate failed: {str(e)}")

    def close_session(self, session):
        """
        Close the session (no-op for certificate auth).

        Args:
            session (dict): Session configuration.
        """
        pass


class Openidconnect(BaseHttp):
    """
    HTTP connector with OpenID Connect authentication.
    """

    def __init__(self, port=443, use_https=True):
        """
        Initialize OpenID Connect connector.

        Args:
            port (int): Default port (default: 443).
            use_https (bool): Whether to use HTTPS (default: True).
        """
        super().__init__(port, use_https)

    def open_session(self, host, port=None, login=None, password=None,
                     client_id=None, client_secret=None, 
                     discovery_url=None, token_endpoint=None,
                     id_token=None, access_token=None):
        """
        Opens a session with OpenID Connect authentication.

        Args:
            host (str): Hostname or IP address.
            port (int): Port. If None, uses default_port.
            login (str): Username for authentication (optional).
            password (str): Password for authentication (optional).
            client_id (str): OpenID Connect client ID.
            client_secret (str): OpenID Connect client secret.
            discovery_url (str): OpenID Connect discovery URL (optional).
            token_endpoint (str): Token endpoint URL (optional).
            id_token (str): Existing ID token (optional).
            access_token (str): Existing access token (optional).

        Returns:
            dict: Session configuration.
        """
        if port is None:
            port = self.default_port
        
        session_data = {
            "host": host,
            "port": port,
            "client_id": client_id,
            "client_secret": client_secret,
            "discovery_url": discovery_url,
            "token_endpoint": token_endpoint,
            "id_token": id_token,
            "access_token": access_token,
            "use_https": self.use_https
        }
        
        # If tokens not provided, try to get them
        if not access_token and token_endpoint and client_id and client_secret:
            try:
                token_data = {
                    "grant_type": "client_credentials",
                    "client_id": client_id,
                    "client_secret": client_secret
                }
                
                if login and password:
                    token_data["grant_type"] = "password"
                    token_data["username"] = login
                    token_data["password"] = password
                
                response = requests.post(token_endpoint, data=token_data)
                response.raise_for_status()
                tokens = response.json()
                
                session_data["access_token"] = tokens.get("access_token")
                session_data["id_token"] = tokens.get("id_token")
            except Exception as e:
                raise Exception(f"Failed to obtain OpenID Connect tokens: {str(e)}")
        
        return session_data

    def execute_command(self, session, command, options=None):
        """
        Execute an HTTP request with OpenID Connect authentication.

        Args:
            session (dict): Session configuration.
            command (str): API endpoint path.
            options (dict): Optional request parameters (method, params, headers, data, json).

        Returns:
            bytes: Response content.
        """
        url = self._build_url(session["host"], session["port"], command)
        
        method = options.get("method", "GET") if options else "GET"
        headers = options.get("headers", {}) if options else {}
        params = options.get("params") if options else None
        data = options.get("data") if options else None
        json_data = options.get("json") if options else None
        
        # Add Bearer token to headers (prefer access_token)
        token = session.get("access_token") or session.get("id_token")
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        response = self._make_request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            data=data,
            json=json_data
        )
        
        return response.content

    def close_session(self, session):
        """
        Close the session (no-op for OpenID Connect).

        Args:
            session (dict): Session configuration.
        """
        pass
