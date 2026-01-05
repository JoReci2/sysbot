"""
Cisco Catalyst Switch Module

This module provides methods for managing and querying Cisco Catalyst switches
using CLI commands over SSH, including version information, interface status,
VLAN configuration, and switch configuration.
"""
from sysbot.utils.engine import ComponentBase
import re


class Catalyst(ComponentBase):
    """Cisco Catalyst switch testing module"""

    def version(self, alias: str, **kwargs) -> str:
        """Get the IOS version of the switch"""
        output = self.execute_command(alias, "show version | include Version", **kwargs)
        return output.strip()

    def hostname(self, alias: str, **kwargs) -> str:
        """Get the hostname of the switch"""
        output = self.execute_command(alias, "show running-config | include hostname", **kwargs)
        return output.replace("hostname ", "").strip()

    def uptime(self, alias: str, **kwargs) -> str:
        """Get the uptime of the switch"""
        output = self.execute_command(alias, "show version | include uptime", **kwargs)
        return output.strip()

    def interfaces(self, alias: str, **kwargs) -> str:
        """Get interface status summary"""
        output = self.execute_command(alias, "show ip interface brief", **kwargs)
        return output

    def interface_status(self, alias: str, interface: str, **kwargs) -> str:
        """Get detailed status of a specific interface"""
        output = self.execute_command(alias, f"show interface {interface}", **kwargs)
        return output

    def vlans(self, alias: str, **kwargs) -> str:
        """Get VLAN configuration"""
        output = self.execute_command(alias, "show vlan brief", **kwargs)
        return output

    def vlan_exists(self, alias: str, vlan_id: int, **kwargs) -> bool:
        """Check if a VLAN exists by verifying the VLAN ID appears in the output"""
        output = self.execute_command(alias, f"show vlan id {vlan_id}", **kwargs)
        # Check for the VLAN ID in the output and absence of error messages
        output_lower = output.lower()
        # Common error messages when VLAN doesn't exist
        error_patterns = ["not found", "does not exist", "invalid", "error"]
        has_errors = any(error in output_lower for error in error_patterns)
        # VLAN should appear in the output (as a standalone number or at line start)
        has_vlan_id = re.search(rf'\b{vlan_id}\b', output) is not None
        return has_vlan_id and not has_errors

    def running_config(self, alias: str, **kwargs) -> str:
        """Get the running configuration"""
        output = self.execute_command(alias, "show running-config", **kwargs)
        return output

    def startup_config(self, alias: str, **kwargs) -> str:
        """Get the startup configuration"""
        output = self.execute_command(alias, "show startup-config", **kwargs)
        return output

    def mac_address_table(self, alias: str, **kwargs) -> str:
        """Get MAC address table"""
        output = self.execute_command(alias, "show mac address-table", **kwargs)
        return output

    def arp_table(self, alias: str, **kwargs) -> str:
        """Get ARP table"""
        output = self.execute_command(alias, "show arp", **kwargs)
        return output

    def routing_table(self, alias: str, **kwargs) -> str:
        """Get IP routing table"""
        output = self.execute_command(alias, "show ip route", **kwargs)
        return output

    def spanning_tree(self, alias: str, **kwargs) -> str:
        """Get spanning tree status"""
        output = self.execute_command(alias, "show spanning-tree summary", **kwargs)
        return output

    def interface_counters(self, alias: str, interface: str, **kwargs) -> str:
        """Get interface counters (errors, packets, etc.)"""
        output = self.execute_command(alias, f"show interface {interface} | include packets|errors", **kwargs)
        return output

    def cdp_neighbors(self, alias: str, **kwargs) -> str:
        """Get CDP neighbors"""
        output = self.execute_command(alias, "show cdp neighbors", **kwargs)
        return output

    def lldp_neighbors(self, alias: str, **kwargs) -> str:
        """Get LLDP neighbors"""
        output = self.execute_command(alias, "show lldp neighbors", **kwargs)
        return output

    def power_inline(self, alias: str, **kwargs) -> str:
        """Get PoE (Power over Ethernet) status"""
        output = self.execute_command(alias, "show power inline", **kwargs)
        return output

    def environment(self, alias: str, **kwargs) -> str:
        """Get environment information (temperature, fans, power supplies)"""
        output = self.execute_command(alias, "show environment all", **kwargs)
        return output

    def inventory(self, alias: str, **kwargs) -> str:
        """Get hardware inventory"""
        output = self.execute_command(alias, "show inventory", **kwargs)
        return output

    def log(self, alias: str, **kwargs) -> str:
        """Get system log"""
        output = self.execute_command(alias, "show logging", **kwargs)
        return output

    def interface_is_up(self, alias: str, interface: str, **kwargs) -> bool:
        """Check if an interface is up (both line protocol and interface status)"""
        output = self.execute_command(alias, f"show interface {interface} | include line protocol", **kwargs)
        # Parse the status line which looks like: "GigabitEthernet1/0/1 is up, line protocol is up"
        # Use regex to match the complete status line format, supporting all interface name formats
        pattern = r'[\w/.]+ is up,\s*line protocol is up'
        return bool(re.search(pattern, output, re.IGNORECASE))

    def save_config(self, alias: str, **kwargs) -> str:
        """Save running configuration to startup configuration"""
        output = self.execute_command(alias, "write memory", **kwargs)
        return output
