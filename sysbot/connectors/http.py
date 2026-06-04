"""
HTTP/HTTPS Connector with Multiple Authentication Methods

This module provides a generic HTTP/HTTPS connector with support for various
authentication methods. Each authentication method is implemented as a separate
self-contained class.
"""

import base64
import hashlib
import hmac
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone

import jwt as jwt_lib
import requests
from requests.adapters import HTTPAdapter
from requests_oauthlib import OAuth1, OAuth2Session
from urllib3.util.retry import Retry

from sysbot.utils.engine import ConnectorInterface

# Whitelist of allowed hash algorithms for HMAC
ALLOWED_HASH_ALGORITHMS = {
    "sha1": hashlib.sha1,
    "sha224": hashlib.sha224,
    "sha256": hashlib.sha256,
    "sha384": hashlib.sha384,
    "sha512": hashlib.sha512,
    "md5": hashlib.md5,
}


class PersistentHttpSession:
    """Persistent HTTP session wrapper with dict-like compatibility."""

    def __init__(self, http_session, data=None, refresh_strategy=None):
        self.http_session = http_session
        self.refresh_strategy = refresh_strategy
        self.created_at = datetime.now(timezone.utc)
        self.last_used = self.created_at
        self._data = dict(data or {})

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    def __contains__(self, key):
        return key in self._data

    def get(self, key, default=None):
        return self._data.get(key, default)

    def update(self, *args, **kwargs):
        self._data.update(*args, **kwargs)

    def keys(self):
        return self._data.keys()

    def items(self):
        return self._data.items()

    def values(self):
        return self._data.values()

    def mark_used(self):
        self.last_used = datetime.now(timezone.utc)

    def close(self):
        self.http_session.close()


class TokenRefreshStrategy(ABC):
    """Strategy interface for token refresh."""

    @abstractmethod
    def is_expired(self, session):
        """Return True when token should be refreshed."""

    @abstractmethod
    def refresh(self, session):
        """Refresh token(s) and update session data."""

    @staticmethod
    def _parse_expiration(value):
        if value is None:
            return None
        if isinstance(value, datetime):
            return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(value, tz=timezone.utc)
        if isinstance(value, str):
            candidate = value.strip()
            if candidate.endswith("Z"):
                candidate = f"{candidate[:-1]}+00:00"
            try:
                parsed = datetime.fromisoformat(candidate)
                return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
            except ValueError:
                return None
        return None

    @staticmethod
    def _require_values(**values):
        missing = [key for key, value in values.items() if not value]
        if missing:
            raise Exception(f"Missing required refresh parameters: {', '.join(missing)}")


class OAuth2RefreshStrategy(TokenRefreshStrategy):
    """OAuth2 token refresh using refresh_token grant."""

    def __init__(self, token_url, client_id, client_secret):
        self.token_url = token_url
        self.client_id = client_id
        self.client_secret = client_secret

    def is_expired(self, session):
        expires_at = self._parse_expiration(session.get("token_expires_at"))
        if not expires_at:
            return False
        return datetime.now(timezone.utc) >= (expires_at - timedelta(seconds=30))

    def refresh(self, session):
        refresh_token = session.get("refresh_token")
        self._require_values(
            refresh_token=refresh_token,
            token_url=self.token_url,
            client_id=self.client_id,
            client_secret=self.client_secret,
        )

        oauth = OAuth2Session(client_id=self.client_id)
        token = oauth.refresh_token(
            token_url=self.token_url,
            refresh_token=refresh_token,
            client_id=self.client_id,
            client_secret=self.client_secret,
        )

        session["access_token"] = token.get("access_token", session.get("access_token"))
        session["refresh_token"] = token.get("refresh_token", session.get("refresh_token"))

        expires_at = token.get("expires_at")
        if expires_at is None:
            expires_in = token.get("expires_in")
            if expires_in is not None:
                expires_at = datetime.now(timezone.utc) + timedelta(seconds=int(expires_in))
        if expires_at is not None:
            session["token_expires_at"] = expires_at


class JwtRefreshStrategy(TokenRefreshStrategy):
    """JWT token refresh by re-signing a new token with the configured secret key."""

    def __init__(self, default_expiration_minutes=60):
        self.default_expiration_minutes = default_expiration_minutes

    def is_expired(self, session):
        token = session.get("token")
        if not token:
            return True

        try:
            payload = jwt_lib.decode(token, options={"verify_signature": False, "verify_exp": False})
        except Exception:
            return True

        exp = payload.get("exp")
        if exp is None:
            return False

        expires_at = self._parse_expiration(exp)
        if not expires_at:
            return False

        return datetime.now(timezone.utc) >= (expires_at - timedelta(seconds=30))

    def refresh(self, session):
        secret_key = session.get("secret_key")
        algorithm = session.get("algorithm", "HS256")
        if not secret_key:
            raise Exception("JWT refresh requires secret_key")

        payload = dict(session.get("payload_template") or {})
        if session.get("login") and "sub" not in payload:
            payload["sub"] = session["login"]

        expiration_minutes = session.get("expiration_minutes", self.default_expiration_minutes)
        now = datetime.now(timezone.utc)
        exp = now + timedelta(minutes=expiration_minutes)
        payload["iat"] = now
        payload["exp"] = exp

        session["token"] = jwt_lib.encode(payload, secret_key, algorithm=algorithm)
        session["token_expires_at"] = exp


class OidcRefreshStrategy(OAuth2RefreshStrategy):
    """OpenID Connect refresh strategy (OAuth2 refresh + id_token update)."""

    def refresh(self, session):
        refresh_token = session.get("refresh_token")
        self._require_values(
            refresh_token=refresh_token,
            token_url=self.token_url,
            client_id=self.client_id,
            client_secret=self.client_secret,
        )

        oauth = OAuth2Session(client_id=self.client_id)
        token = oauth.refresh_token(
            token_url=self.token_url,
            refresh_token=refresh_token,
            client_id=self.client_id,
            client_secret=self.client_secret,
        )

        session["access_token"] = token.get("access_token", session.get("access_token"))
        session["refresh_token"] = token.get("refresh_token", session.get("refresh_token"))
        session["id_token"] = token.get("id_token", session.get("id_token"))

        expires_at = token.get("expires_at")
        if expires_at is None:
            expires_in = token.get("expires_in")
            if expires_in is not None:
                expires_at = datetime.now(timezone.utc) + timedelta(seconds=int(expires_in))
        if expires_at is not None:
            session["token_expires_at"] = expires_at


class BaseHttp(ConnectorInterface):
    """Base class for HTTP/HTTPS connectors providing common functionality."""

    def __init__(self, port=443, use_https=True, request_timeout=30):
        super().__init__()
        self.default_port = port
        self.use_https = use_https
        self.request_timeout = request_timeout

    def _create_http_session(self):
        logging.getLogger("urllib3.util.retry").setLevel(logging.ERROR)
        http_session = requests.Session()
        retry_strategy = Retry(
            total=3,
            connect=3,
            read=3,
            status=3,
            backoff_factor=0.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset({"HEAD", "GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"}),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=10)
        http_session.mount("http://", adapter)
        http_session.mount("https://", adapter)
        return http_session

    def _create_persistent_session(self, data, refresh_strategy=None):
        return PersistentHttpSession(self._create_http_session(), data=data, refresh_strategy=refresh_strategy)

    def _build_url(self, host, port, endpoint):
        protocol = "https" if self.use_https else "http"
        return f"{protocol}://{host}:{port}{endpoint}"

    def _apply_auth_headers(self, session, headers, request_kwargs):
        """Hook for authentication-specific header or request mutation."""

    def _make_request(self, session, method, url, headers=None, params=None, data=None, json=None, verify=True, **request_kwargs):
        headers = dict(headers or {})

        try:
            refresh_strategy = getattr(session, "refresh_strategy", None)
            if refresh_strategy and refresh_strategy.is_expired(session):
                try:
                    refresh_strategy.refresh(session)
                except Exception as e:
                    raise Exception(f"Token refresh failed: {str(e)}")

            self._apply_auth_headers(session, headers, request_kwargs)

            response = session.http_session.request(
                method=method.upper(),
                url=url,
                headers=headers,
                params=params,
                data=data,
                json=json,
                verify=verify,
                timeout=self.request_timeout,
                **request_kwargs,
            )
            response.raise_for_status()
            session.mark_used()
            return response
        except requests.exceptions.RequestException as e:
            raise Exception(f"HTTP request failed: {str(e)}")

    def close_session(self, session):
        if isinstance(session, PersistentHttpSession):
            session.close()


class Apikey(BaseHttp):
    """HTTP connector with API Key authentication."""

    def __init__(self, port=443, use_https=True, request_timeout=30):
        super().__init__(port, use_https, request_timeout=request_timeout)

    def open_session(
        self,
        host,
        port=None,
        login=None,
        password=None,
        api_key=None,
        api_key_header="X-API-Key",
        api_key_in_query=False,
        verify_ssl=True,
    ):
        if port is None:
            port = self.default_port

        return self._create_persistent_session(
            {
                "host": host,
                "port": port,
                "api_key": api_key,
                "api_key_header": api_key_header,
                "api_key_in_query": api_key_in_query,
                "use_https": self.use_https,
                "verify_ssl": verify_ssl,
            }
        )

    def _apply_auth_headers(self, session, headers, request_kwargs):
        if not session.get("api_key_in_query") and session.get("api_key") is not None:
            headers[session["api_key_header"]] = session["api_key"]

    def execute_command(self, session, command, options=None):
        url = self._build_url(session["host"], session["port"], command)
        method = options.get("method", "GET") if options else "GET"
        headers = dict(options.get("headers", {}) if options else {})
        params = dict(options.get("params", {}) if options else {})
        data = options.get("data") if options else None
        json_data = options.get("json") if options else None
        verify = options.get("verify", session.get("verify_ssl", True)) if options else session.get("verify_ssl", True)

        if session.get("api_key_in_query") and session.get("api_key") is not None:
            params[session["api_key_header"]] = session["api_key"]

        response = self._make_request(session, method, url, headers=headers, params=params, data=data, json=json_data, verify=verify)
        return response.content


class Basicauth(BaseHttp):
    """HTTP connector with Basic Authentication (username/password)."""

    def __init__(self, port=443, use_https=True, request_timeout=30):
        super().__init__(port, use_https, request_timeout=request_timeout)

    def open_session(self, host, port=None, login=None, password=None, verify_ssl=True):
        if port is None:
            port = self.default_port

        return self._create_persistent_session(
            {
                "host": host,
                "port": port,
                "login": login,
                "password": password,
                "use_https": self.use_https,
                "verify_ssl": verify_ssl,
            }
        )

    def _apply_auth_headers(self, session, headers, request_kwargs):
        credentials = f"{session.get('login', '')}:{session.get('password', '')}".encode()
        headers["Authorization"] = f"Basic {base64.b64encode(credentials).decode()}"

    def execute_command(self, session, command, options=None):
        url = self._build_url(session["host"], session["port"], command)
        method = options.get("method", "GET") if options else "GET"
        headers = options.get("headers") if options else None
        params = options.get("params") if options else None
        data = options.get("data") if options else None
        json_data = options.get("json") if options else None
        verify = options.get("verify", session.get("verify_ssl", True)) if options else session.get("verify_ssl", True)

        response = self._make_request(session, method, url, headers=headers, params=params, data=data, json=json_data, verify=verify)
        return response.content


class Oauth1(BaseHttp):
    """HTTP connector with OAuth 1.0 authentication."""

    def __init__(self, port=443, use_https=True, request_timeout=30):
        super().__init__(port, use_https, request_timeout=request_timeout)

    def open_session(
        self,
        host,
        port=None,
        login=None,
        password=None,
        client_key=None,
        client_secret=None,
        resource_owner_key=None,
        resource_owner_secret=None,
        verify_ssl=True,
    ):
        if port is None:
            port = self.default_port

        return self._create_persistent_session(
            {
                "host": host,
                "port": port,
                "client_key": client_key,
                "client_secret": client_secret,
                "resource_owner_key": resource_owner_key,
                "resource_owner_secret": resource_owner_secret,
                "use_https": self.use_https,
                "verify_ssl": verify_ssl,
            }
        )

    def execute_command(self, session, command, options=None):
        url = self._build_url(session["host"], session["port"], command)
        method = options.get("method", "GET") if options else "GET"
        headers = options.get("headers") if options else None
        params = options.get("params") if options else None
        data = options.get("data") if options else None
        json_data = options.get("json") if options else None
        verify = options.get("verify", session.get("verify_ssl", True)) if options else session.get("verify_ssl", True)

        auth = OAuth1(
            session["client_key"],
            session["client_secret"],
            session["resource_owner_key"],
            session["resource_owner_secret"],
        )
        response = self._make_request(
            session,
            method,
            url,
            headers=headers,
            params=params,
            data=data,
            json=json_data,
            verify=verify,
            auth=auth,
        )
        return response.content


class Oauth2(BaseHttp):
    """HTTP connector with OAuth 2.0 authentication."""

    def __init__(self, port=443, use_https=True, request_timeout=30):
        super().__init__(port, use_https, request_timeout=request_timeout)

    def open_session(
        self,
        host,
        port=None,
        login=None,
        password=None,
        client_id=None,
        client_secret=None,
        token_url=None,
        access_token=None,
        refresh_token=None,
        verify_ssl=True,
    ):
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
            "use_https": self.use_https,
            "verify_ssl": verify_ssl,
        }

        if not access_token and token_url and client_id and client_secret:
            try:
                oauth = OAuth2Session(client_id)
                token = oauth.fetch_token(token_url=token_url, client_id=client_id, client_secret=client_secret)
                session_data["access_token"] = token.get("access_token")
                session_data["refresh_token"] = token.get("refresh_token")
                expires_at = token.get("expires_at")
                if expires_at is None:
                    expires_in = token.get("expires_in")
                    if expires_in is not None:
                        expires_at = datetime.now(timezone.utc) + timedelta(seconds=int(expires_in))
                if expires_at is not None:
                    session_data["token_expires_at"] = expires_at
            except Exception as e:
                raise Exception(f"Failed to obtain OAuth 2.0 token: {str(e)}")

        refresh_strategy = None
        if token_url and client_id and client_secret and session_data.get("refresh_token"):
            refresh_strategy = OAuth2RefreshStrategy(token_url=token_url, client_id=client_id, client_secret=client_secret)

        return self._create_persistent_session(session_data, refresh_strategy=refresh_strategy)

    def _apply_auth_headers(self, session, headers, request_kwargs):
        if session.get("access_token"):
            headers["Authorization"] = f"Bearer {session['access_token']}"

    def execute_command(self, session, command, options=None):
        url = self._build_url(session["host"], session["port"], command)
        method = options.get("method", "GET") if options else "GET"
        headers = dict(options.get("headers", {}) if options else {})
        params = options.get("params") if options else None
        data = options.get("data") if options else None
        json_data = options.get("json") if options else None
        verify = options.get("verify", session.get("verify_ssl", True)) if options else session.get("verify_ssl", True)

        response = self._make_request(session, method, url, headers=headers, params=params, data=data, json=json_data, verify=verify)
        return response.content


class Jwt(BaseHttp):
    """HTTP connector with JWT (JSON Web Token) authentication."""

    def __init__(self, port=443, use_https=True, request_timeout=30):
        super().__init__(port, use_https, request_timeout=request_timeout)

    def open_session(
        self,
        host,
        port=None,
        login=None,
        password=None,
        secret_key=None,
        algorithm="HS256",
        token=None,
        payload=None,
        expiration_minutes=60,
        verify_ssl=True,
    ):
        if port is None:
            port = self.default_port

        payload_template = dict(payload or {})
        token_expires_at = None

        if not token and secret_key:
            issued_payload = dict(payload_template)
            if login:
                issued_payload["sub"] = login

            now = datetime.now(timezone.utc)
            token_expires_at = now + timedelta(minutes=expiration_minutes)
            issued_payload["exp"] = token_expires_at
            issued_payload["iat"] = now
            token = jwt_lib.encode(issued_payload, secret_key, algorithm=algorithm)
        elif token:
            try:
                decoded = jwt_lib.decode(token, options={"verify_signature": False, "verify_exp": False})
                token_expires_at = decoded.get("exp")
            except Exception:
                token_expires_at = None

        session_data = {
            "host": host,
            "port": port,
            "login": login,
            "token": token,
            "secret_key": secret_key,
            "algorithm": algorithm,
            "payload_template": payload_template,
            "expiration_minutes": expiration_minutes,
            "token_expires_at": token_expires_at,
            "use_https": self.use_https,
            "verify_ssl": verify_ssl,
        }

        refresh_strategy = JwtRefreshStrategy(default_expiration_minutes=expiration_minutes) if secret_key else None
        return self._create_persistent_session(session_data, refresh_strategy=refresh_strategy)

    def _apply_auth_headers(self, session, headers, request_kwargs):
        if session.get("token"):
            headers["Authorization"] = f"Bearer {session['token']}"

    def execute_command(self, session, command, options=None):
        url = self._build_url(session["host"], session["port"], command)
        method = options.get("method", "GET") if options else "GET"
        headers = dict(options.get("headers", {}) if options else {})
        params = options.get("params") if options else None
        data = options.get("data") if options else None
        json_data = options.get("json") if options else None
        verify = options.get("verify", session.get("verify_ssl", True)) if options else session.get("verify_ssl", True)

        response = self._make_request(session, method, url, headers=headers, params=params, data=data, json=json_data, verify=verify)
        return response.content


class Saml(BaseHttp):
    """HTTP connector with SAML authentication."""

    def __init__(self, port=443, use_https=True, request_timeout=30):
        super().__init__(port, use_https, request_timeout=request_timeout)

    def open_session(self, host, port=None, login=None, password=None, saml_token=None, saml_header="X-SAML-Token", verify_ssl=True):
        if port is None:
            port = self.default_port

        return self._create_persistent_session(
            {
                "host": host,
                "port": port,
                "saml_token": saml_token,
                "saml_header": saml_header,
                "use_https": self.use_https,
                "verify_ssl": verify_ssl,
            }
        )

    def _apply_auth_headers(self, session, headers, request_kwargs):
        if session.get("saml_token") is not None:
            headers[session["saml_header"]] = session["saml_token"]

    def execute_command(self, session, command, options=None):
        url = self._build_url(session["host"], session["port"], command)
        method = options.get("method", "GET") if options else "GET"
        headers = dict(options.get("headers", {}) if options else {})
        params = options.get("params") if options else None
        data = options.get("data") if options else None
        json_data = options.get("json") if options else None
        verify = options.get("verify", session.get("verify_ssl", True)) if options else session.get("verify_ssl", True)

        response = self._make_request(session, method, url, headers=headers, params=params, data=data, json=json_data, verify=verify)
        return response.content


class Hmac(BaseHttp):
    """HTTP connector with HMAC authentication."""

    def __init__(self, port=443, use_https=True, request_timeout=30):
        super().__init__(port, use_https, request_timeout=request_timeout)

    def open_session(
        self,
        host,
        port=None,
        login=None,
        password=None,
        secret_key=None,
        algorithm="sha256",
        signature_header="X-Signature",
        timestamp_header="X-Timestamp",
        verify_ssl=True,
    ):
        if port is None:
            port = self.default_port

        return self._create_persistent_session(
            {
                "host": host,
                "port": port,
                "access_key": login,
                "secret_key": secret_key,
                "algorithm": algorithm,
                "signature_header": signature_header,
                "timestamp_header": timestamp_header,
                "use_https": self.use_https,
                "verify_ssl": verify_ssl,
            }
        )

    def _generate_signature(self, secret_key, algorithm, method, path, timestamp, body=""):
        if algorithm not in ALLOWED_HASH_ALGORITHMS:
            raise ValueError(f"Hash algorithm '{algorithm}' is not allowed. Must be one of: {', '.join(ALLOWED_HASH_ALGORITHMS.keys())}")

        string_to_sign = f"{method}\n{path}\n{timestamp}\n{body}"
        hash_func = ALLOWED_HASH_ALGORITHMS[algorithm]
        signature = hmac.new(secret_key.encode(), string_to_sign.encode(), hash_func).digest()
        return base64.b64encode(signature).decode()

    def execute_command(self, session, command, options=None):
        url = self._build_url(session["host"], session["port"], command)
        method = options.get("method", "GET") if options else "GET"
        headers = dict(options.get("headers", {}) if options else {})
        params = options.get("params") if options else None
        data = options.get("data") if options else None
        json_data = options.get("json") if options else None
        verify = options.get("verify", session.get("verify_ssl", True)) if options else session.get("verify_ssl", True)

        timestamp = str(int(datetime.now(timezone.utc).timestamp()))
        body = ""
        if data:
            body = str(data)
        elif json_data:
            body = json.dumps(json_data)

        signature = self._generate_signature(session["secret_key"], session["algorithm"], method, command, timestamp, body)

        if session.get("access_key"):
            headers["X-Access-Key"] = session["access_key"]
        headers[session["timestamp_header"]] = timestamp
        headers[session["signature_header"]] = signature

        response = self._make_request(session, method, url, headers=headers, params=params, data=data, json=json_data, verify=verify)
        return response.content


class Certificate(BaseHttp):
    """HTTP connector with Client Certificate authentication (mutual TLS)."""

    def __init__(self, port=443, use_https=True, request_timeout=30):
        super().__init__(port, use_https, request_timeout=request_timeout)

    def open_session(
        self,
        host,
        port=None,
        login=None,
        password=None,
        cert_file=None,
        key_file=None,
        ca_bundle=None,
        verify_ssl=True,
    ):
        if port is None:
            port = self.default_port

        return self._create_persistent_session(
            {
                "host": host,
                "port": port,
                "cert_file": cert_file,
                "key_file": key_file,
                "ca_bundle": ca_bundle,
                "key_password": password,
                "use_https": self.use_https,
                "verify_ssl": verify_ssl,
            }
        )

    def execute_command(self, session, command, options=None):
        url = self._build_url(session["host"], session["port"], command)
        method = options.get("method", "GET") if options else "GET"
        headers = options.get("headers") if options else None
        params = options.get("params") if options else None
        data = options.get("data") if options else None
        json_data = options.get("json") if options else None

        cert = (session["cert_file"], session["key_file"]) if session.get("key_file") else session["cert_file"]

        if options and "verify" in options:
            verify = options["verify"]
        elif session.get("ca_bundle"):
            verify = session["ca_bundle"]
        else:
            verify = session.get("verify_ssl", True)

        response = self._make_request(
            session,
            method,
            url,
            headers=headers,
            params=params,
            data=data,
            json=json_data,
            verify=verify,
            cert=cert,
        )
        return response.content


class Openidconnect(BaseHttp):
    """HTTP connector with OpenID Connect authentication."""

    def __init__(self, port=443, use_https=True, request_timeout=30):
        super().__init__(port, use_https, request_timeout=request_timeout)

    def open_session(
        self,
        host,
        port=None,
        login=None,
        password=None,
        client_id=None,
        client_secret=None,
        discovery_url=None,
        token_endpoint=None,
        id_token=None,
        access_token=None,
        refresh_token=None,
        verify_ssl=True,
    ):
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
            "refresh_token": refresh_token,
            "use_https": self.use_https,
            "verify_ssl": verify_ssl,
        }

        if not access_token and token_endpoint and client_id and client_secret:
            try:
                token_data = {
                    "grant_type": "client_credentials",
                    "client_id": client_id,
                    "client_secret": client_secret,
                }
                if login and password:
                    token_data["grant_type"] = "password"
                    token_data["username"] = login
                    token_data["password"] = password

                temp_session = self._create_http_session()
                try:
                    response = temp_session.post(
                        token_endpoint,
                        data=token_data,
                        verify=verify_ssl,
                        timeout=self.request_timeout,
                    )
                    response.raise_for_status()
                    tokens = response.json()
                finally:
                    temp_session.close()

                session_data["access_token"] = tokens.get("access_token")
                session_data["id_token"] = tokens.get("id_token")
                session_data["refresh_token"] = tokens.get("refresh_token")
                expires_at = tokens.get("expires_at")
                if expires_at is None:
                    expires_in = tokens.get("expires_in")
                    if expires_in is not None:
                        expires_at = datetime.now(timezone.utc) + timedelta(seconds=int(expires_in))
                if expires_at is not None:
                    session_data["token_expires_at"] = expires_at
            except Exception as e:
                raise Exception(f"Failed to obtain OpenID Connect tokens: {str(e)}")

        refresh_strategy = None
        if token_endpoint and client_id and client_secret and session_data.get("refresh_token"):
            refresh_strategy = OidcRefreshStrategy(token_url=token_endpoint, client_id=client_id, client_secret=client_secret)

        return self._create_persistent_session(session_data, refresh_strategy=refresh_strategy)

    def _apply_auth_headers(self, session, headers, request_kwargs):
        token = session.get("access_token") or session.get("id_token")
        if token:
            headers["Authorization"] = f"Bearer {token}"

    def execute_command(self, session, command, options=None):
        url = self._build_url(session["host"], session["port"], command)
        method = options.get("method", "GET") if options else "GET"
        headers = dict(options.get("headers", {}) if options else {})
        params = options.get("params") if options else None
        data = options.get("data") if options else None
        json_data = options.get("json") if options else None
        verify = options.get("verify", session.get("verify_ssl", True)) if options else session.get("verify_ssl", True)

        response = self._make_request(session, method, url, headers=headers, params=params, data=data, json=json_data, verify=verify)
        return response.content
