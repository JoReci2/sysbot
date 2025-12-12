import requests
from requests.auth import HTTPBasicAuth
from sysbot.utils.engine import ConnectorInterface
from sysbot.connectors.config import DEFAULT_PORTS, create_response


class Basicauth(ConnectorInterface):
    """
    HTTP/HTTPS connector with basic authentication using requests library.
    Supports RESTful API interactions with basic auth credentials.
    """

    def open_session(self, host, port=None, login=None, password=None, use_https=True, **kwargs):
        """
        Opens a session to an API with basic auth.
        
        Args:
            host (str): Hostname or IP address
            port (int): Port number (default: 443 for HTTPS, 80 for HTTP)
            login (str): Username for basic auth
            password (str): Password for basic auth
            use_https (bool): Whether to use HTTPS (default: True)
            **kwargs: Additional session parameters
            
        Returns:
            dict: Session information for API calls
        """
        if port is None:
            port = DEFAULT_PORTS["https"] if use_https else DEFAULT_PORTS["http"]
            
        protocol = "https" if use_https else "http"
        
        session_data = {
            "host": host,
            "port": port,
            "login": login,
            "password": password,
            "protocol": protocol,
            "verify_ssl": kwargs.get("verify_ssl", False),
            "timeout": kwargs.get("timeout", 30)
        }
        return session_data

    def execute_command(self, session, command, options=None, method="GET", **kwargs):
        """
        Executes an HTTP request to an API with basic auth.
        
        Args:
            session (dict): Session dictionary containing connection info
            command (str): The API endpoint/path to call
            options (dict): Request options (params, data, json, headers, etc.)
            method (str): HTTP method (GET, POST, PUT, DELETE, etc.)
            **kwargs: Additional request parameters
            
        Returns:
            dict: Standardized response with StatusCode, Result, Error, and Metadata
        """
        if not session:
            return create_response(
                status_code=1,
                result=None,
                error="Invalid session"
            )
            
        base_url = f"{session['protocol']}://{session['host']}:{session['port']}{command}"
        basic = HTTPBasicAuth(session["login"], session["password"])
        
        # Merge options with kwargs
        request_params = options.copy() if options else {}
        request_params.update(kwargs)
        
        # Set defaults
        verify_ssl = request_params.pop("verify_ssl", session.get("verify_ssl", False))
        timeout = request_params.pop("timeout", session.get("timeout", 30))
        
        try:
            response = requests.request(
                method=method.upper(),
                url=base_url,
                auth=basic,
                verify=verify_ssl,
                timeout=timeout,
                **request_params
            )
            
            # Try to parse as JSON, fallback to text
            try:
                result_data = response.json()
            except ValueError:
                result_data = response.text
            
            return create_response(
                status_code=response.status_code,
                result=result_data,
                error=None if response.status_code < 400 else f"HTTP {response.status_code}: {response.reason}",
                metadata={
                    "host": session["host"],
                    "port": session["port"],
                    "method": method,
                    "endpoint": command,
                    "headers": dict(response.headers),
                    "elapsed": response.elapsed.total_seconds()
                }
            )
        except requests.exceptions.Timeout:
            return create_response(
                status_code=1,
                result=None,
                error=f"Request timeout after {timeout} seconds",
                metadata={"host": session["host"], "endpoint": command}
            )
        except requests.exceptions.ConnectionError as e:
            return create_response(
                status_code=1,
                result=None,
                error=f"Connection error: {str(e)}",
                metadata={"host": session["host"], "endpoint": command}
            )
        except Exception as e:
            return create_response(
                status_code=1,
                result=None,
                error=f"Failed to execute command: {str(e)}",
                metadata={"host": session["host"], "endpoint": command}
            )

    def close_session(self, session):
        """
        Closes the session to the API with basic auth.
        Note: HTTP connections are stateless, so this is mostly a no-op.
        
        Args:
            session (dict): Session dictionary
        """
        # HTTP is stateless, no persistent connection to close
        pass
