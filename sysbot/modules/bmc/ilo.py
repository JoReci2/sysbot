"""
HPE iLO (Integrated Lights-Out) Module

This module provides methods for interacting with HPE iLO BMC systems via Redfish API.
It supports common operations such as retrieving system information, power management,
and firmware information.
"""

from sysbot.utils.engine import ComponentBase


class Ilo(ComponentBase):
    """
    HPE iLO module for BMC system management.
    
    This class provides methods to interact with HPE iLO systems using Redfish API.
    All methods require an alias to identify the established Redfish session.
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
        endpoint = f"/Systems/{system_id}"
        response = self.execute_command(alias, endpoint, method="GET")
        return response

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
        endpoint = f"/Systems/{system_id}/Actions/ComputerSystem.Reset"
        body = {"ResetType": action}
        response = self.execute_command(alias, endpoint, method="POST", body=body)
        return response

    def get_firmware_version(self, alias: str, manager_id: str = "1") -> dict:
        """
        Get iLO firmware version information.

        Args:
            alias (str): The session alias for the iLO connection.
            manager_id (str): Manager identifier (default: "1").

        Returns:
            dict: Firmware version information.
        """
        endpoint = f"/Managers/{manager_id}"
        response = self.execute_command(alias, endpoint, method="GET")
        firmware_info = {
            "FirmwareVersion": response.get("FirmwareVersion"),
            "Model": response.get("Model"),
            "Name": response.get("Name")
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
        endpoint = f"/Systems/{system_id}/Processors"
        response = self.execute_command(alias, endpoint, method="GET")
        return response

    def get_memory(self, alias: str, system_id: str = "1") -> dict:
        """
        Get memory information.

        Args:
            alias (str): The session alias for the iLO connection.
            system_id (str): System identifier (default: "1").

        Returns:
            dict: Memory information.
        """
        endpoint = f"/Systems/{system_id}/Memory"
        response = self.execute_command(alias, endpoint, method="GET")
        return response

    def get_network_adapters(self, alias: str, system_id: str = "1") -> dict:
        """
        Get network adapter information.

        Args:
            alias (str): The session alias for the iLO connection.
            system_id (str): System identifier (default: "1").

        Returns:
            dict: Network adapter information.
        """
        endpoint = f"/Systems/{system_id}/NetworkAdapters"
        response = self.execute_command(alias, endpoint, method="GET")
        return response

    def get_storage(self, alias: str, system_id: str = "1") -> dict:
        """
        Get storage information.

        Args:
            alias (str): The session alias for the iLO connection.
            system_id (str): System identifier (default: "1").

        Returns:
            dict: Storage information.
        """
        endpoint = f"/Systems/{system_id}/Storage"
        response = self.execute_command(alias, endpoint, method="GET")
        return response

    def get_thermal_info(self, alias: str, chassis_id: str = "1") -> dict:
        """
        Get thermal (temperature and fans) information.

        Args:
            alias (str): The session alias for the iLO connection.
            chassis_id (str): Chassis identifier (default: "1").

        Returns:
            dict: Thermal information including temperatures and fans.
        """
        endpoint = f"/Chassis/{chassis_id}/Thermal"
        response = self.execute_command(alias, endpoint, method="GET")
        return response

    def get_power_info(self, alias: str, chassis_id: str = "1") -> dict:
        """
        Get power supply and power consumption information.

        Args:
            alias (str): The session alias for the iLO connection.
            chassis_id (str): Chassis identifier (default: "1").

        Returns:
            dict: Power information.
        """
        endpoint = f"/Chassis/{chassis_id}/Power"
        response = self.execute_command(alias, endpoint, method="GET")
        return response

    def get_event_log(self, alias: str, manager_id: str = "1") -> dict:
        """
        Get iLO event log entries.

        Args:
            alias (str): The session alias for the iLO connection.
            manager_id (str): Manager identifier (default: "1").

        Returns:
            dict: Event log information.
        """
        endpoint = f"/Managers/{manager_id}/LogServices/IEL/Entries"
        response = self.execute_command(alias, endpoint, method="GET")
        return response

    def clear_event_log(self, alias: str, manager_id: str = "1") -> dict:
        """
        Clear the iLO event log.

        Args:
            alias (str): The session alias for the iLO connection.
            manager_id (str): Manager identifier (default: "1").

        Returns:
            dict: Response from the clear operation.
        """
        endpoint = f"/Managers/{manager_id}/LogServices/IEL/Actions/LogService.ClearLog"
        response = self.execute_command(alias, endpoint, method="POST", body={})
        return response
