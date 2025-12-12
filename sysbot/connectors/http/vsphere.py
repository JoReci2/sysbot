from pyVim.connect import SmartConnect, Disconnect
from sysbot.utils.engine import ConnectorInterface
from sysbot.connectors.config import DEFAULT_PORTS, create_response


class Vsphere(ConnectorInterface):
    """
    VMware vSphere connector using pyVmomi library.
    Supports connections to ESXi hosts and vCenter servers.
    """

    def open_session(self, host, port=None, login=None, password=None, **kwargs):
        """
        Opens a session to a VMware vSphere system.

        Args:
            host (str): Hostname or IP address of the VMware system.
            port (int): Port of the VMware service (default: 443).
            login (str): Username for the session.
            password (str): Password for the session.
            **kwargs: Additional connection parameters

        Returns:
            dict: Session information including authenticated VMware client.

        Raises:
            Exception: If there is an error opening the session.
        """
        if port is None:
            port = DEFAULT_PORTS["https"]
            
        try:
            client = SmartConnect(
                host=host,
                port=port,
                user=login,
                pwd=password,
                disableSslCertValidation=kwargs.get("disable_ssl_verification", True),
            )
            
            return {
                "client": client,
                "host": host,
                "port": port
            }
        except Exception as e:
            raise Exception(f"Failed to open VMware session to {host}:{port}: {str(e)}")

    def execute_command(self, session, command, options=None, **kwargs):
        """
        Returns the vSphere session for direct API usage.
        
        Note: vSphere uses direct API calls rather than command execution.
        This method returns the session object for use with vSphere modules.

        Args:
            session (dict): The VMware session dictionary.
            command (str): Not used for vSphere (kept for interface compatibility)
            options (dict): Not used for vSphere (kept for interface compatibility)
            **kwargs: Additional parameters

        Returns:
            dict: Standardized response containing the vSphere client session
        """
        if not session or "client" not in session:
            return create_response(
                status_code=1,
                result=None,
                error="Invalid session: vSphere client not found"
            )
            
        try:
            return create_response(
                status_code=0,
                result=session["client"],
                error=None,
                metadata={
                    "host": session.get("host"),
                    "port": session.get("port"),
                    "note": "Use the Result field to access vSphere API directly"
                }
            )
        except Exception as e:
            return create_response(
                status_code=1,
                result=None,
                error=f"Failed to execute command: {str(e)}",
                metadata={"host": session.get("host")}
            )

    def close_session(self, session):
        """
        Closes an open session to a VMware system.

        Args:
            session (dict): The VMware session dictionary to close.

        Raises:
            Exception: If there is an error closing the session.
        """
        if session and "client" in session:
            try:
                Disconnect(session["client"])
            except Exception as e:
                raise Exception(f"Failed to close VMware session: {str(e)}")
