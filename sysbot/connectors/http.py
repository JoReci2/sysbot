"""
HTTP/HTTPS Connector with Multiple Authentication Methods

This module provides a generic HTTP/HTTPS connector with support for various
authentication methods. Each authentication method is implemented as a separate
self-contained class.
"""

import json
import requests
import hmac
import hashlib
import base64
import jwt as jwt_lib
from datetime import datetime, timedelta, timezone
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth1, OAuth2Session
from sysbot.utils.engine import ConnectorInterface

# Whitelist of allowed hash algorithms for HMAC
ALLOWED_HASH_ALGORITHMS = {
    "sha1": hashlib.sha1,
    "sha224": hashlib.sha224,
    "sha256": hashlib.sha256,
    "sha384": hashlib.sha384,
    "sha512": hashlib.sha512,
    "md5": hashlib.md5
}


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

    def _make_request(self, method, url, auth=None, headers=None, params=None, data=None, json=None, verify=True):
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
            verify (bool): Whether to verify SSL certificates (default: True).

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

    def test_connection(self, session, test_endpoint="/", test_method="GET", verify=True):
        """
        Test the connection by making a request to a test endpoint.

        Args:
            session (dict): Session configuration containing host, port, and auth details.
            test_endpoint (str): Endpoint path to test (default: "/").
            test_method (str): HTTP method to use for testing (default: "GET").
            verify (bool): Whether to verify SSL certificates (default: True).

        Returns:
            bool: True if connection test succeeds.

        Raises:
            Exception: If the connection test fails.
        """
        # This method should be overridden by child classes to include auth
        # but provides a basic structure
        url = self._build_url(session["host"], session["port"], test_endpoint)
        try:
            self._make_request(
                method=test_method,
                url=url,
                verify=verify
            )
            return True
        except Exception as e:
            raise Exception(f"Connection test failed: {str(e)}")


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
                     api_key_header="X-API-Key", api_key_in_query=False,
                     test_endpoint=None, test_method="GET", verify=True):
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
            test_endpoint (str): Optional endpoint to test the connection (e.g., "/api/health").
            test_method (str): HTTP method for connection test (default: "GET").
            verify (bool): Whether to verify SSL certificates during test (default: True).

        Returns:
            dict: Session configuration.

        Raises:
            Exception: If test_endpoint is provided and connection test fails.
        """
        if port is None:
            port = self.default_port

        session = {
            "host": host,
            "port": port,
            "api_key": api_key,
            "api_key_header": api_key_header,
            "api_key_in_query": api_key_in_query,
            "use_https": self.use_https
        }

        # Test connection if test_endpoint is provided
        if test_endpoint:
            self._test_connection_with_auth(session, test_endpoint, test_method, verify)

        return session

    def _test_connection_with_auth(self, session, test_endpoint, test_method, verify):
        """
        Test connection with API key authentication.

        Args:
            session (dict): Session configuration.
            test_endpoint (str): Endpoint to test.
            test_method (str): HTTP method for test.
            verify (bool): Whether to verify SSL certificates.

        Raises:
            Exception: If connection test fails.
        """
        url = self._build_url(session["host"], session["port"], test_endpoint)
        headers = {}
        params = {}

        if session.get("api_key_in_query"):
            params[session["api_key_header"]] = session["api_key"]
        else:
            headers[session["api_key_header"]] = session["api_key"]

        self._make_request(
            method=test_method,
            url=url,
            headers=headers,
            params=params,
            verify=verify
        )

    def execute_command(self, session, command, options=None):
        """
        Execute an HTTP request with API key authentication.

        Args:
            session (dict): Session configuration.
            command (str): API endpoint path.
            options (dict): Optional request parameters:
                - method (str): HTTP method (default: GET)
                - params (dict): URL query parameters
                - headers (dict): HTTP headers
                - data: Request body data
                - json: JSON request body
                - verify (bool): Verify SSL certificates (default: True)

        Returns:
            bytes: Response content.
        """
        url = self._build_url(session["host"], session["port"], command)

        method = options.get("method", "GET") if options else "GET"
        headers = options.get("headers", {}) if options else {}
        params = options.get("params", {}) if options else {}
        data = options.get("data") if options else None
        json_data = options.get("json") if options else None
        verify = options.get("verify", True) if options else True

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
            json=json_data,
            verify=verify
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

    def open_session(self, host, port=None, login=None, password=None,
                     test_endpoint=None, test_method="GET", verify=True):
        """
        Opens a session with Basic authentication.

        Args:
            host (str): Hostname or IP address.
            port (int): Port. If None, uses default_port.
            login (str): Username.
            password (str): Password.
            test_endpoint (str): Optional endpoint to test the connection (e.g., "/api/health").
            test_method (str): HTTP method for connection test (default: "GET").
            verify (bool): Whether to verify SSL certificates during test (default: True).

        Returns:
            dict: Session configuration.

        Raises:
            Exception: If test_endpoint is provided and connection test fails.
        """
        if port is None:
            port = self.default_port

        session = {
            "host": host,
            "port": port,
            "login": login,
            "password": password,
            "use_https": self.use_https
        }

        # Test connection if test_endpoint is provided
        if test_endpoint:
            self._test_connection_with_auth(session, test_endpoint, test_method, verify)

        return session

    def _test_connection_with_auth(self, session, test_endpoint, test_method, verify):
        """
        Test connection with Basic authentication.

        Args:
            session (dict): Session configuration.
            test_endpoint (str): Endpoint to test.
            test_method (str): HTTP method for test.
            verify (bool): Whether to verify SSL certificates.

        Raises:
            Exception: If connection test fails.
        """
        url = self._build_url(session["host"], session["port"], test_endpoint)
        auth = HTTPBasicAuth(session["login"], session["password"])

        self._make_request(
            method=test_method,
            url=url,
            auth=auth,
            verify=verify
        )

    def execute_command(self, session, command, options=None):
        """
        Execute an HTTP request with Basic authentication.

        Args:
            session (dict): Session configuration.
            command (str): API endpoint path.
            options (dict): Optional request parameters:
                - method (str): HTTP method (default: GET)
                - params (dict): URL query parameters
                - headers (dict): HTTP headers
                - data: Request body data
                - json: JSON request body
                - verify (bool): Verify SSL certificates (default: True)

        Returns:
            bytes: Response content.
        """
        url = self._build_url(session["host"], session["port"], command)

        method = options.get("method", "GET") if options else "GET"
        headers = options.get("headers") if options else None
        params = options.get("params") if options else None
        data = options.get("data") if options else None
        json_data = options.get("json") if options else None
        verify = options.get("verify", True) if options else True

        auth = HTTPBasicAuth(session["login"], session["password"])

        response = self._make_request(
            method=method,
            url=url,
            auth=auth,
            headers=headers,
            params=params,
            data=data,
            json=json_data,
            verify=verify
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
                     resource_owner_key=None, resource_owner_secret=None,
                     test_endpoint=None, test_method="GET", verify=True):
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
            test_endpoint (str): Optional endpoint to test the connection (e.g., "/api/health").
            test_method (str): HTTP method for connection test (default: "GET").
            verify (bool): Whether to verify SSL certificates during test (default: True).

        Returns:
            dict: Session configuration.

        Raises:
            Exception: If test_endpoint is provided and connection test fails.
        """
        if port is None:
            port = self.default_port

        session = {
            "host": host,
            "port": port,
            "client_key": client_key,
            "client_secret": client_secret,
            "resource_owner_key": resource_owner_key,
            "resource_owner_secret": resource_owner_secret,
            "use_https": self.use_https
        }

        # Test connection if test_endpoint is provided
        if test_endpoint:
            self._test_connection_with_auth(session, test_endpoint, test_method, verify)

        return session

    def _test_connection_with_auth(self, session, test_endpoint, test_method, verify):
        """
        Test connection with OAuth 1.0 authentication.

        Args:
            session (dict): Session configuration.
            test_endpoint (str): Endpoint to test.
            test_method (str): HTTP method for test.
            verify (bool): Whether to verify SSL certificates.

        Raises:
            Exception: If connection test fails.
        """
        url = self._build_url(session["host"], session["port"], test_endpoint)
        auth = OAuth1(
            session["client_key"],
            session["client_secret"],
            session["resource_owner_key"],
            session["resource_owner_secret"]
        )

        self._make_request(
            method=test_method,
            url=url,
            auth=auth,
            verify=verify
        )

    def execute_command(self, session, command, options=None):
        """
        Execute an HTTP request with OAuth 1.0 authentication.

        Args:
            session (dict): Session configuration.
            command (str): API endpoint path.
            options (dict): Optional request parameters:
                - method (str): HTTP method (default: GET)
                - params (dict): URL query parameters
                - headers (dict): HTTP headers
                - data: Request body data
                - json: JSON request body
                - verify (bool): Verify SSL certificates (default: True)

        Returns:
            bytes: Response content.
        """
        url = self._build_url(session["host"], session["port"], command)

        method = options.get("method", "GET") if options else "GET"
        headers = options.get("headers") if options else None
        params = options.get("params") if options else None
        data = options.get("data") if options else None
        json_data = options.get("json") if options else None
        verify = options.get("verify", True) if options else True

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
            json=json_data,
            verify=verify
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
                     access_token=None, refresh_token=None,
                     test_endpoint=None, test_method="GET", verify=True):
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
            test_endpoint (str): Optional endpoint to test the connection (e.g., "/api/health").
            test_method (str): HTTP method for connection test (default: "GET").
            verify (bool): Whether to verify SSL certificates during test (default: True).

        Returns:
            dict: Session configuration.

        Raises:
            Exception: If test_endpoint is provided and connection test fails.
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

        # Test connection if test_endpoint is provided
        if test_endpoint:
            self._test_connection_with_auth(session_data, test_endpoint, test_method, verify)

        return session_data

    def _test_connection_with_auth(self, session, test_endpoint, test_method, verify):
        """
        Test connection with OAuth 2.0 authentication.

        Args:
            session (dict): Session configuration.
            test_endpoint (str): Endpoint to test.
            test_method (str): HTTP method for test.
            verify (bool): Whether to verify SSL certificates.

        Raises:
            Exception: If connection test fails.
        """
        url = self._build_url(session["host"], session["port"], test_endpoint)
        headers = {"Authorization": f"Bearer {session['access_token']}"}

        self._make_request(
            method=test_method,
            url=url,
            headers=headers,
            verify=verify
        )

    def execute_command(self, session, command, options=None):
        """
        Execute an HTTP request with OAuth 2.0 authentication.

        Args:
            session (dict): Session configuration.
            command (str): API endpoint path.
            options (dict): Optional request parameters:
                - method (str): HTTP method (default: GET)
                - params (dict): URL query parameters
                - headers (dict): HTTP headers
                - data: Request body data
                - json: JSON request body
                - verify (bool): Verify SSL certificates (default: True)

        Returns:
            bytes: Response content.
        """
        url = self._build_url(session["host"], session["port"], command)

        method = options.get("method", "GET") if options else "GET"
        headers = options.get("headers", {}) if options else {}
        params = options.get("params") if options else None
        data = options.get("data") if options else None
        json_data = options.get("json") if options else None
        verify = options.get("verify", True) if options else True

        # Add Bearer token to headers
        headers["Authorization"] = f"Bearer {session['access_token']}"

        response = self._make_request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            data=data,
            json=json_data,
            verify=verify
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
                     payload=None, expiration_minutes=60,
                     test_endpoint=None, test_method="GET", verify=True):
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
            test_endpoint (str): Optional endpoint to test the connection (e.g., "/api/health").
            test_method (str): HTTP method for connection test (default: "GET").
            verify (bool): Whether to verify SSL certificates during test (default: True).

        Returns:
            dict: Session configuration.

        Raises:
            Exception: If test_endpoint is provided and connection test fails.
        """
        if port is None:
            port = self.default_port

        # Generate token if not provided
        if not token and secret_key:
            if payload is None:
                payload = {}

            if login:
                payload["sub"] = login

            now = datetime.now(timezone.utc)
            payload["exp"] = now + timedelta(minutes=expiration_minutes)
            payload["iat"] = now

            token = jwt_lib.encode(payload, secret_key, algorithm=algorithm)

        session = {
            "host": host,
            "port": port,
            "token": token,
            "secret_key": secret_key,
            "algorithm": algorithm,
            "use_https": self.use_https
        }

        # Test connection if test_endpoint is provided
        if test_endpoint:
            self._test_connection_with_auth(session, test_endpoint, test_method, verify)

        return session

    def _test_connection_with_auth(self, session, test_endpoint, test_method, verify):
        """
        Test connection with JWT authentication.

        Args:
            session (dict): Session configuration.
            test_endpoint (str): Endpoint to test.
            test_method (str): HTTP method for test.
            verify (bool): Whether to verify SSL certificates.

        Raises:
            Exception: If connection test fails.
        """
        url = self._build_url(session["host"], session["port"], test_endpoint)
        headers = {"Authorization": f"Bearer {session['token']}"}

        self._make_request(
            method=test_method,
            url=url,
            headers=headers,
            verify=verify
        )

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
        verify = options.get("verify", True) if options else True

        # Add JWT to headers
        headers["Authorization"] = f"Bearer {session['token']}"

        response = self._make_request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            data=data,
            json=json_data,
            verify=verify
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
                     saml_token=None, saml_header="X-SAML-Token",
                     test_endpoint=None, test_method="GET", verify=True):
        """
        Opens a session with SAML authentication.

        Args:
            host (str): Hostname or IP address.
            port (int): Port. If None, uses default_port.
            login (str): Not used (for compatibility).
            password (str): Not used (for compatibility).
            saml_token (str): SAML assertion/token.
            saml_header (str): Header name for SAML token (default: X-SAML-Token).
            test_endpoint (str): Optional endpoint to test the connection (e.g., "/api/health").
            test_method (str): HTTP method for connection test (default: "GET").
            verify (bool): Whether to verify SSL certificates during test (default: True).

        Returns:
            dict: Session configuration.

        Raises:
            Exception: If test_endpoint is provided and connection test fails.
        """
        if port is None:
            port = self.default_port

        session = {
            "host": host,
            "port": port,
            "saml_token": saml_token,
            "saml_header": saml_header,
            "use_https": self.use_https
        }

        # Test connection if test_endpoint is provided
        if test_endpoint:
            self._test_connection_with_auth(session, test_endpoint, test_method, verify)

        return session

    def _test_connection_with_auth(self, session, test_endpoint, test_method, verify):
        """
        Test connection with SAML authentication.

        Args:
            session (dict): Session configuration.
            test_endpoint (str): Endpoint to test.
            test_method (str): HTTP method for test.
            verify (bool): Whether to verify SSL certificates.

        Raises:
            Exception: If connection test fails.
        """
        url = self._build_url(session["host"], session["port"], test_endpoint)
        headers = {session["saml_header"]: session["saml_token"]}

        self._make_request(
            method=test_method,
            url=url,
            headers=headers,
            verify=verify
        )

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
        verify = options.get("verify", True) if options else True

        # Add SAML token to headers
        headers[session["saml_header"]] = session["saml_token"]

        response = self._make_request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            data=data,
            json=json_data,
            verify=verify
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
                     timestamp_header="X-Timestamp",
                     test_endpoint=None, test_method="GET", verify=True):
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
            test_endpoint (str): Optional endpoint to test the connection (e.g., "/api/health").
            test_method (str): HTTP method for connection test (default: "GET").
            verify (bool): Whether to verify SSL certificates during test (default: True).

        Returns:
            dict: Session configuration.

        Raises:
            Exception: If test_endpoint is provided and connection test fails.
        """
        if port is None:
            port = self.default_port

        session = {
            "host": host,
            "port": port,
            "access_key": login,
            "secret_key": secret_key,
            "algorithm": algorithm,
            "signature_header": signature_header,
            "timestamp_header": timestamp_header,
            "use_https": self.use_https
        }

        # Test connection if test_endpoint is provided
        if test_endpoint:
            self._test_connection_with_auth(session, test_endpoint, test_method, verify)

        return session

    def _test_connection_with_auth(self, session, test_endpoint, test_method, verify):
        """
        Test connection with HMAC authentication.

        Args:
            session (dict): Session configuration.
            test_endpoint (str): Endpoint to test.
            test_method (str): HTTP method for test.
            verify (bool): Whether to verify SSL certificates.

        Raises:
            Exception: If connection test fails.
        """
        url = self._build_url(session["host"], session["port"], test_endpoint)

        # Generate timestamp
        timestamp = str(int(datetime.now(timezone.utc).timestamp()))

        # Generate signature
        signature = self._generate_signature(
            session["secret_key"],
            session["algorithm"],
            test_method,
            test_endpoint,
            timestamp,
            ""
        )

        headers = {
            session["signature_header"]: signature,
            session["timestamp_header"]: timestamp
        }

        if session.get("access_key"):
            headers["X-Access-Key"] = session["access_key"]

        self._make_request(
            method=test_method,
            url=url,
            headers=headers,
            verify=verify
        )

    def _generate_signature(self, secret_key, algorithm, method, path, timestamp, body=""):
        """
        Generate HMAC signature for the request.

        Args:
            secret_key (str): The secret key for signing.
            algorithm (str): Hash algorithm name (must be in whitelist).
            method (str): HTTP method.
            path (str): Request path.
            timestamp (str): Request timestamp.
            body (str): Request body.

        Returns:
            str: Base64-encoded HMAC signature.

        Raises:
            ValueError: If algorithm is not in the whitelist.
        """
        # Validate algorithm against whitelist
        if algorithm not in ALLOWED_HASH_ALGORITHMS:
            allowed = ', '.join(ALLOWED_HASH_ALGORITHMS.keys())
            raise ValueError(f"Hash algorithm '{algorithm}' is not allowed. Must be one of: {allowed}")

        # Create string to sign
        string_to_sign = f"{method}\n{path}\n{timestamp}\n{body}"

        # Get hash function from whitelist
        hash_func = ALLOWED_HASH_ALGORITHMS[algorithm]

        # Generate HMAC
        signature = hmac.new(
            secret_key.encode(),
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
        verify = options.get("verify", True) if options else True

        # Generate timestamp
        timestamp = str(int(datetime.now(timezone.utc).timestamp()))

        # Generate signature
        body = ""
        if data:
            body = str(data)
        elif json_data:
            body = json.dumps(json_data)

        signature = self._generate_signature(
            session["secret_key"],
            session["algorithm"],
            method,
            command,
            timestamp,
            body
        )

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
            json=json_data,
            verify=verify
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
                     cert_file=None, key_file=None, ca_bundle=None,
                     test_endpoint=None, test_method="GET", verify=True):
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
            test_endpoint (str): Optional endpoint to test the connection (e.g., "/api/health").
            test_method (str): HTTP method for connection test (default: "GET").
            verify (bool): Whether to verify SSL certificates during test (default: True).

        Returns:
            dict: Session configuration.

        Raises:
            Exception: If test_endpoint is provided and connection test fails.
        """
        if port is None:
            port = self.default_port

        session = {
            "host": host,
            "port": port,
            "cert_file": cert_file,
            "key_file": key_file,
            "ca_bundle": ca_bundle,
            "key_password": password,
            "use_https": self.use_https
        }

        # Test connection if test_endpoint is provided
        if test_endpoint:
            self._test_connection_with_auth(session, test_endpoint, test_method, verify)

        return session

    def _test_connection_with_auth(self, session, test_endpoint, test_method, verify):
        """
        Test connection with certificate authentication.

        Args:
            session (dict): Session configuration.
            test_endpoint (str): Endpoint to test.
            test_method (str): HTTP method for test.
            verify (bool): Whether to verify SSL certificates.

        Raises:
            Exception: If connection test fails.
        """
        url = self._build_url(session["host"], session["port"], test_endpoint)

        # Prepare certificate tuple
        if session.get("key_file"):
            cert = (session["cert_file"], session["key_file"])
        else:
            cert = session["cert_file"]

        # Use CA bundle if provided
        verify_param = session.get("ca_bundle") if session.get("ca_bundle") else verify

        try:
            response = requests.request(
                method=test_method.upper(),
                url=url,
                cert=cert,
                verify=verify_param
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Connection test failed: {str(e)}")

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
        # If ca_bundle is provided, use it; otherwise default to True for security
        # Can be overridden via options
        if options and "verify" in options:
            verify = options["verify"]
        elif session.get("ca_bundle"):
            verify = session["ca_bundle"]
        else:
            verify = True

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
                     id_token=None, access_token=None,
                     test_endpoint=None, test_method="GET", verify=True):
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
            test_endpoint (str): Optional endpoint to test the connection (e.g., "/api/health").
            test_method (str): HTTP method for connection test (default: "GET").
            verify (bool): Whether to verify SSL certificates during test (default: True).

        Returns:
            dict: Session configuration.

        Raises:
            Exception: If test_endpoint is provided and connection test fails.
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

        # Test connection if test_endpoint is provided
        if test_endpoint:
            self._test_connection_with_auth(session_data, test_endpoint, test_method, verify)

        return session_data

    def _test_connection_with_auth(self, session, test_endpoint, test_method, verify):
        """
        Test connection with OpenID Connect authentication.

        Args:
            session (dict): Session configuration.
            test_endpoint (str): Endpoint to test.
            test_method (str): HTTP method for test.
            verify (bool): Whether to verify SSL certificates.

        Raises:
            Exception: If connection test fails.
        """
        url = self._build_url(session["host"], session["port"], test_endpoint)

        # Use access_token or id_token (prefer access_token)
        token = session.get("access_token") or session.get("id_token")
        if token:
            headers = {"Authorization": f"Bearer {token}"}
        else:
            headers = {}

        self._make_request(
            method=test_method,
            url=url,
            headers=headers,
            verify=verify
        )

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
        verify = options.get("verify", True) if options else True

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
            json=json_data,
            verify=verify
        )

        return response.content

    def close_session(self, session):
        """
        Close the session (no-op for OpenID Connect).

        Args:
            session (dict): Session configuration.
        """
        pass
