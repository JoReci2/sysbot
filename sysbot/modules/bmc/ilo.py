"""
HPE iLO (Integrated Lights-Out) Module

This module provides methods for interacting with HPE iLO BMC systems via Redfish API.
It supports common operations such as retrieving system information, power management,
and firmware information.

Note: This module uses the HTTP connector with Basic authentication.
Sessions should be opened with protocol="http" and product="basicauth".
"""

import json
from sysbot.utils.engine import ComponentBase

# Default Redfish API prefix for most BMC implementations
REDFISH_PREFIX = "/redfish/v1"


class Ilo(ComponentBase):
    """
    HPE iLO module for BMC system management.
    
    This class provides methods to interact with HPE iLO systems using Redfish API
    via the HTTP connector with Basic authentication.
    All methods require an alias to identify the established HTTP session.
    """

    def get_system_info(self, alias: str, system_id: str = "1") -> dict:
        """
        Get general system information from iLO.

        Args:
            alias (str): The session alias for the iLO connection.
            system_id (str): System identifier (default: "1").

        Returns:
            dict: System information including model, serial number, manufacturer, etc.
        """
        endpoint = f"{REDFISH_PREFIX}/Systems/{system_id}"
        response = self.execute_command(alias, endpoint, options={"method": "GET"})
        return json.loads(response.decode())

    def get_power_state(self, alias: str, system_id: str = "1") -> str:
        """
        Get the current power state of the system.

        Args:
            alias (str): The session alias for the iLO connection.
            system_id (str): System identifier (default: "1").

        Returns:
            str: Power state (e.g., "On", "Off", "PoweringOn", "PoweringOff").
        """
        system_info = self.get_system_info(alias, system_id)
        return system_info.get("PowerState", "Unknown")

    def set_power_state(self, alias: str, action: str, system_id: str = "1") -> dict:
        """
        Set the power state of the system.

        Args:
            alias (str): The session alias for the iLO connection.
            action (str): Power action ("On", "ForceOff", "GracefulShutdown", 
                         "ForceRestart", "Nmi", "PushPowerButton").
            system_id (str): System identifier (default: "1").

        Returns:
            dict: Response from the power operation.
        """
        endpoint = f"{REDFISH_PREFIX}/Systems/{system_id}/Actions/ComputerSystem.Reset"
        body = {"ResetType": action}
        response = self.execute_command(alias, endpoint, options={"method": "POST", "json": body})
        return json.loads(response.decode()) if response else {}

    def get_firmware_version(self, alias: str, manager_id: str = "1") -> dict:
        """
        Get iLO firmware version information.

        Args:
            alias (str): The session alias for the iLO connection.
            manager_id (str): Manager identifier (default: "1").

        Returns:
            dict: Firmware version information.
        """
        endpoint = f"{REDFISH_PREFIX}/Managers/{manager_id}"
        response = self.execute_command(alias, endpoint, options={"method": "GET"})
        data = json.loads(response.decode())
        firmware_info = {
            "FirmwareVersion": data.get("FirmwareVersion"),
            "Model": data.get("Model"),
            "Name": data.get("Name")
        }
        return firmware_info

    def get_bios_version(self, alias: str, system_id: str = "1") -> str:
        """
        Get BIOS version information.

        Args:
            alias (str): The session alias for the iLO connection.
            system_id (str): System identifier (default: "1").

        Returns:
            str: BIOS version.
        """
        system_info = self.get_system_info(alias, system_id)
        return system_info.get("BiosVersion", "Unknown")

    def get_processors(self, alias: str, system_id: str = "1") -> dict:
        """
        Get processor information.

        Args:
            alias (str): The session alias for the iLO connection.
            system_id (str): System identifier (default: "1").

        Returns:
            dict: Processor information.
        """
        endpoint = f"{REDFISH_PREFIX}/Systems/{system_id}/Processors"
        response = self.execute_command(alias, endpoint, options={"method": "GET"})
        return json.loads(response.decode())

    def get_memory(self, alias: str, system_id: str = "1") -> dict:
        """
        Get memory information.

        Args:
            alias (str): The session alias for the iLO connection.
            system_id (str): System identifier (default: "1").

        Returns:
            dict: Memory information.
        """
        endpoint = f"{REDFISH_PREFIX}/Systems/{system_id}/Memory"
        response = self.execute_command(alias, endpoint, options={"method": "GET"})
        return json.loads(response.decode())

    def get_network_adapters(self, alias: str, system_id: str = "1") -> dict:
        """
        Get network adapter information.

        Args:
            alias (str): The session alias for the iLO connection.
            system_id (str): System identifier (default: "1").

        Returns:
            dict: Network adapter information.
        """
        endpoint = f"{REDFISH_PREFIX}/Systems/{system_id}/NetworkAdapters"
        response = self.execute_command(alias, endpoint, options={"method": "GET"})
        return json.loads(response.decode())

    def get_storage(self, alias: str, system_id: str = "1") -> dict:
        """
        Get storage information.

        Args:
            alias (str): The session alias for the iLO connection.
            system_id (str): System identifier (default: "1").

        Returns:
            dict: Storage information.
        """
        endpoint = f"{REDFISH_PREFIX}/Systems/{system_id}/Storage"
        response = self.execute_command(alias, endpoint, options={"method": "GET"})
        return json.loads(response.decode())

    def get_thermal_info(self, alias: str, chassis_id: str = "1") -> dict:
        """
        Get thermal (temperature and fans) information.

        Args:
            alias (str): The session alias for the iLO connection.
            chassis_id (str): Chassis identifier (default: "1").

        Returns:
            dict: Thermal information including temperatures and fans.
        """
        endpoint = f"{REDFISH_PREFIX}/Chassis/{chassis_id}/Thermal"
        response = self.execute_command(alias, endpoint, options={"method": "GET"})
        return json.loads(response.decode())

    def get_power_info(self, alias: str, chassis_id: str = "1") -> dict:
        """
        Get power supply and power consumption information.

        Args:
            alias (str): The session alias for the iLO connection.
            chassis_id (str): Chassis identifier (default: "1").

        Returns:
            dict: Power information.
        """
        endpoint = f"{REDFISH_PREFIX}/Chassis/{chassis_id}/Power"
        response = self.execute_command(alias, endpoint, options={"method": "GET"})
        return json.loads(response.decode())

    def get_event_log(self, alias: str, manager_id: str = "1") -> dict:
        """
        Get iLO event log entries.

        Args:
            alias (str): The session alias for the iLO connection.
            manager_id (str): Manager identifier (default: "1").

        Returns:
            dict: Event log information.
        """
        endpoint = f"{REDFISH_PREFIX}/Managers/{manager_id}/LogServices/IEL/Entries"
        response = self.execute_command(alias, endpoint, options={"method": "GET"})
        return json.loads(response.decode())

    def clear_event_log(self, alias: str, manager_id: str = "1") -> dict:
        """
        Clear the iLO event log.

        Args:
            alias (str): The session alias for the iLO connection.
            manager_id (str): Manager identifier (default: "1").

        Returns:
            dict: Response from the clear operation.
        """
        endpoint = f"{REDFISH_PREFIX}/Managers/{manager_id}/LogServices/IEL/Actions/LogService.ClearLog"
        response = self.execute_command(alias, endpoint, options={"method": "POST", "json": {}})
        return json.loads(response.decode()) if response else {}

    def get_ntp_source(self, alias: str, manager_id: str = "1") -> list:
        """
        Get NTP server configuration from iLO.

        Args:
            alias (str): The session alias for the iLO connection.
            manager_id (str): Manager identifier (default: "1").

        Returns:
            list: List of NTP servers configured.
        """
        endpoint = f"{REDFISH_PREFIX}/Managers/{manager_id}/NetworkProtocol"
        response = self.execute_command(alias, endpoint, options={"method": "GET"})
        data = json.loads(response.decode())
        return data.get("NTP", {}).get("NTPServers", [])

    def get_timezone(self, alias: str, manager_id: str = "1") -> str:
        """
        Get timezone configuration from iLO.

        Args:
            alias (str): The session alias for the iLO connection.
            manager_id (str): Manager identifier (default: "1").

        Returns:
            str: Timezone configuration.
        """
        endpoint = f"{REDFISH_PREFIX}/Managers/{manager_id}"
        response = self.execute_command(alias, endpoint, options={"method": "GET"})
        data = json.loads(response.decode())
        # Check for timezone in different possible locations
        timezone = data.get("DateTime", {}).get("TimeZone") if isinstance(data.get("DateTime"), dict) else None
        if not timezone:
            timezone = data.get("DateTimeLocalOffset", "Unknown")
        return timezone

    def get_utc_datetime(self, alias: str, manager_id: str = "1") -> str:
        """
        Get current UTC datetime from iLO.

        Args:
            alias (str): The session alias for the iLO connection.
            manager_id (str): Manager identifier (default: "1").

        Returns:
            str: Current UTC datetime in ISO format.
        """
        endpoint = f"{REDFISH_PREFIX}/Managers/{manager_id}"
        response = self.execute_command(alias, endpoint, options={"method": "GET"})
        data = json.loads(response.decode())
        return data.get("DateTime", "Unknown")

    def get_language(self, alias: str, manager_id: str = "1") -> str:
        """
        Get language configuration from iLO.

        Args:
            alias (str): The session alias for the iLO connection.
            manager_id (str): Manager identifier (default: "1").

        Returns:
            str: Language configuration.
        """
        endpoint = f"{REDFISH_PREFIX}/Managers/{manager_id}"
        response = self.execute_command(alias, endpoint, options={"method": "GET"})
        data = json.loads(response.decode())
        # Language might be in different locations depending on iLO version
        language = data.get("Oem", {}).get("Hp", {}).get("Language") or \
                   data.get("Oem", {}).get("Hpe", {}).get("Language") or \
                   "Unknown"
        return language
