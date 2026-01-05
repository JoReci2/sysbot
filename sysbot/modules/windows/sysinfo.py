"""
Windows System Information Module

This module provides methods for retrieving system information on Windows systems,
including hostname, domain, timezone, hardware details, and operating system
information using PowerShell and WMI.
"""
from sysbot.utils.engine import ComponentBase
import json


class Sysinfo(ComponentBase):
    """Windows system information retrieval class using PowerShell and WMI."""

    def hostname(self, alias: str, **kwargs) -> str:
        """
        Get the system hostname (short name).

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            System hostname without domain.
        """
        return self.execute_command(alias, "$env:computername", **kwargs)

    def fqdn(self, alias: str, **kwargs) -> str:
        """
        Get the fully qualified domain name (FQDN).

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            Fully qualified domain name.
        """
        return self.execute_command(
            alias,
            "[System.Net.Dns]::GetHostByName($env:computerName).HostName",
            **kwargs,
        )

    def domain(self, alias: str, **kwargs) -> str:
        """
        Get the DNS domain name.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            DNS domain name.
        """
        return self.execute_command(alias, "$env:USERDNSDOMAIN", **kwargs)

    def timezone(self, alias: str, **kwargs) -> str:
        """
        Get the system timezone offset.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            Timezone offset from UTC (e.g., +01:00, -05:00).
        """
        return self.execute_command(
            alias, "(Get-Date).ToUniversalTime().ToString('zzz')", **kwargs
        )

    def datetime_utc(self, alias: str, **kwargs) -> str:
        """
        Get current date and time in UTC.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            Current date and time formatted with timezone offset.
        """
        return self.execute_command(
            alias,
            "[DateTimeOffset]::Now.ToString('dddd, MMMM dd, yyyy hh:mm:ss tt zzz')",
            **kwargs,
        )

    def env(self, alias: str, name: str, **kwargs) -> str:
        """
        Get the value of an environment variable.

        Args:
            alias: Session alias for the connection.
            name: Name of the environment variable.
            **kwargs: Additional command execution options.

        Returns:
            Value of the environment variable.
        """
        return self.execute_command(
            alias, f"[Environment]::GetEnvironmentVariable('{name}')", **kwargs
        )

    def win32_process(self, alias: str, **kwargs) -> dict:
        """
        Get process information using WMI Win32_Process class.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing process information including ProcessName, PageFileUsage,
            PeakVirtualSize, and PrivatePageCount.
        """
        command = "Get-WmiObject -Class Win32_Process | Select-Object ProcessName, PageFileUsage, PeakVirtualSize, PrivatePageCount | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def win32_operatingsystem(self, alias: str, **kwargs) -> dict:
        """
        Get operating system information using WMI Win32_OperatingSystem class.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing OS information including Caption, InstallDate, Version,
            BootDevice, BuildNumber, MUILanguages, SystemDirectory, SystemDrive, and WindowsDirectory.
        """
        command = "Get-WmiObject -Class Win32_OperatingSystem | Select-Object Caption, InstallDate, Version, BootDevice, BuildNumber, MUILanguages, SystemDirectory, SystemDrive, WindowsDirectory | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def win32_physicalmemory(self, alias: str, **kwargs) -> dict:
        """
        Get physical memory information using WMI Win32_PhysicalMemory class.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing physical memory Capacity information.
        """
        command = "Get-WmiObject -Class Win32_PhysicalMemory | Select-Object Capacity | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def win32_processor(self, alias: str, **kwargs) -> dict:
        """
        Get processor information using WMI Win32_Processor class.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing CPU information including Caption, DeviceID, MaxClockSpeed,
            NumberOfCores, and NumberOfLogicalProcessors.
        """
        command = "Get-WmiObject -class Win32_Processor | Select-Object Caption, DeviceID, MaxClockSpeed, NumberOfCores, NumberOfLogicalProcessors | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def win32_diskdrive(self, alias: str, **kwargs) -> dict:
        """
        Get disk drive information using WMI Win32_DiskDrive class.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing disk drive information including Name, Caption, Partitions,
            BytesPerSector, Size, and SerialNumber.
        """
        command = "Get-WmiObject -Class Win32_DiskDrive | Select-Object Name, Caption, Partitions, BytesPerSector, Size, SerialNumber | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def win32_logicaldisk(self, alias: str, **kwargs) -> dict:
        """
        Get logical disk information using WMI Win32_LogicalDisk class.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing logical disk information including Caption, FileSystem, and Size.
        """
        command = "Get-WmiObject -Class Win32_LogicalDisk | Select-Object Caption, FileSystem, Size | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def win32_service(self, alias: str, **kwargs) -> dict:
        """
        Get service information using WMI Win32_Service class.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing service information including Name, DisplayName, StartName,
            State, and StartMode.
        """
        command = "Get-WmiObject -Class Win32_Service | Select-Object Name, DisplayName, StartName, State, StartMode | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def roles(self, alias: str, **kwargs) -> dict:
        """
        Get Windows roles and features.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing installed roles and features information.
        """
        output = self.execute_command(
            alias, "Get-WindowsFeature | ConvertTo-Json", **kwargs
        )
        return json.loads(output)

    def software(self, alias: str, **kwargs) -> list:
        """
        Get list of installed software from the registry.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            List of installed software display names.
        """
        output = self.execute_command(
            alias,
            "(Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | Where-Object {$_.DisplayName -ne $null}).DisplayName",
            **kwargs,
        )
        return output.splitlines()

    def registry(self, alias: str, path: str, **kwargs) -> list:
        """
        Get registry key properties.

        Args:
            alias: Session alias for the connection.
            path: Registry path to query.
            **kwargs: Additional command execution options.

        Returns:
            List of property names in the registry key.
        """
        output = self.execute_command(
            alias,
            f"Get-Item -Path Registry::{path} | Select-Object -ExpandProperty Property",
            **kwargs,
        )
        return output.splitlines()
