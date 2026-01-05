"""
Linux System Information Module

This module provides methods for retrieving system information on Linux systems,
including OS details, hostname, uptime, kernel version, CPU, memory, and
hardware information.
"""
from sysbot.utils.engine import ComponentBase
import json
from datetime import datetime, timezone


class Sysinfo(ComponentBase):
    """System information retrieval class for Linux systems."""

    def os_release(self, alias: str, **kwargs) -> dict:
        """
        Get operating system release information.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing OS release information from /etc/os-release.
        """
        output = self.execute_command(alias, "cat /etc/os-release", **kwargs)
        data = {}
        for line in output.splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                if "=" in line:
                    key, value = line.split("=", 1)
                    data[key] = value.strip("\"'")
        return data

    def hostname(self, alias: str, **kwargs) -> str:
        """
        Get the system hostname (short name).

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            System hostname without domain.
        """
        return self.execute_command(alias, "hostname -s", **kwargs)

    def fqdn(self, alias: str, **kwargs) -> str:
        """
        Get the fully qualified domain name (FQDN).

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            Fully qualified domain name.
        """
        return self.execute_command(alias, "hostname -f", **kwargs)

    def domain(self, alias: str, **kwargs) -> str:
        """
        Get the DNS domain name.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            DNS domain name.
        """
        return self.execute_command(alias, "hostname -d", **kwargs)

    def uptime(self, alias: str, **kwargs) -> str:
        """
        Get system uptime in a human-readable format.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            System uptime as a formatted string.
        """
        return self.execute_command(alias, "uptime --pretty", **kwargs)

    def kernel(self, alias: str, **kwargs) -> str:
        """
        Get the kernel version.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            Kernel version string.
        """
        return self.execute_command(alias, "uname -r", **kwargs)

    def architecture(self, alias: str, **kwargs) -> str:
        """
        Get the system architecture.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            System architecture (e.g., x86_64, aarch64).
        """
        return self.execute_command(alias, "uname -m", **kwargs)

    def ram(self, alias: str, **kwargs) -> dict:
        """
        Get memory (RAM) information.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing memory statistics with values and units.
        """
        output = self.execute_command(alias, "cat /proc/meminfo", **kwargs)
        data = {}
        for line in output.splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            key = (
                key.strip().lower().replace("(", "").replace(")", "").replace(" ", "_")
            )
            parts = value.strip().split()
            val = int(parts[0]) if parts else 0
            unit = parts[1] if len(parts) > 1 else None

            data[key] = {"value": val, "unit": unit}

        return data

    def cpu(self, alias: str, **kwargs) -> dict:
        """
        Get CPU information.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing CPU details from lscpu.
        """
        output = self.execute_command(alias, "lscpu", **kwargs)
        lines = output.splitlines()
        cpu_info = {}
        for line in lines:
            if ":" in line:
                key, value = line.split(":", 1)
                cpu_info[key.strip()] = value.strip()
        return cpu_info

    def keyboard(self, alias: str, **kwargs) -> str:
        """
        Get the keyboard layout.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            Keyboard layout name.
        """
        return self.execute_command(
            alias, "localectl | grep Keymap | awk '{print $3}' | tr -d ' '", **kwargs
        )

    def timezone(self, alias: str, **kwargs) -> str:
        """
        Get the system timezone.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            Timezone name (e.g., America/New_York, Europe/Paris).
        """
        return self.execute_command(
            alias,
            "timedatectl | grep 'Time zone' | awk '{print $3}' | tr -d ' '",
            **kwargs,
        )

    def datetime_utc(self, alias: str) -> str:
        """
        Get current date and time in UTC.

        Args:
            alias: Session alias for the connection.

        Returns:
            Date and time in UTC formatted as 'YYYY/MM/DD HH:MM'.
        """
        output = self.execute_command(alias, "date '+%a %b %d %H:%M:%S %Y %z'")
        current_time = datetime.strptime(output, "%a %b %d %H:%M:%S %Y %z")
        utc_time = current_time.astimezone(timezone.utc)
        return utc_time.strftime("%Y/%m/%d %H:%M")

    def env(self, alias: str, **kwargs) -> dict:
        """
        Get environment variables.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary of environment variables and their values.
        """
        output = self.execute_command(alias, "printenv", **kwargs)
        env_vars = {}
        for line in output.splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                env_vars[key] = value.strip()
        return env_vars

    def process(self, alias: str, **kwargs) -> dict:
        """
        Get list of running processes.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary of processes indexed by PID with user, command, CPU, and memory info.
        """
        output = self.execute_command(
            alias, "ps -Aww -o pid,user,comm,pcpu,pmem", **kwargs
        )
        processes = {}
        for line in output.splitlines()[1:]:
            if line:
                pid, user, comm, pcpu, pmem = line.split(None, 4)
                processes[pid] = {
                    "user": user,
                    "command": comm,
                    "cpu": pcpu,
                    "memory": pmem,
                }
        return processes

    def lsblk(self, alias: str, **kwargs) -> dict:
        """
        Get block device information.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing block device information in JSON format.
        """
        output = self.execute_command(alias, "lsblk --json", **kwargs)
        return json.loads(output)

    def sysctl(self, alias: str, variable: str) -> str:
        """
        Get a kernel parameter value using sysctl.

        Args:
            alias: Session alias for the connection.
            variable: Sysctl variable name (e.g., 'kernel.hostname').

        Returns:
            Value of the sysctl variable.
        """
        return self.execute_command(alias, f"sysctl -n {variable}")

    def dns(self, alias: str) -> list[str]:
        """
        Get configured DNS nameservers.

        Args:
            alias: Session alias for the connection.

        Returns:
            List of DNS server IP addresses.
        """
        output = self.execute_command(alias, "cat /etc/resolv.conf")
        result = [
            srv.replace("nameserver ", "")
            for srv in output.splitlines()
            if srv.startswith("nameserver")
        ]
        return result

    def ntp_server(self, alias: str) -> list[str]:
        """
        Get configured NTP servers from chrony configuration.

        Args:
            alias: Session alias for the connection.

        Returns:
            List of NTP server addresses.
        """
        output = self.execute_command(alias, "cat /etc/chrony.conf")
        result = [
            srv.replace("server ", "")
            for srv in output.splitlines()
            if srv.startswith("server ")
        ]
        result = [srv.split(" ")[0] if " " in srv else srv for srv in result]
        return result
