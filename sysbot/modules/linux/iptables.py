"""
Iptables Module

This module provides methods for querying and managing iptables firewall rules
on Linux systems, including listing rules, checking chains, and viewing policies.
"""
from sysbot.utils.engine import ComponentBase
from typing import List, Dict


class Iptables(ComponentBase):
    """Iptables firewall management class for Linux systems."""

    def list_rules(self, alias: str, table: str = "filter", **kwargs) -> str:
        """
        List all iptables rules for a specific table.

        Args:
            alias: Session alias for the connection.
            table: Table name (filter, nat, mangle, raw, security). Defaults to "filter".
            **kwargs: Additional command execution options.

        Returns:
            String containing all rules in the specified table.
        """
        return self.execute_command(
            alias, f"iptables -t {table} -L -n -v", **kwargs
        )

    def list_rules_line_numbers(
        self, alias: str, table: str = "filter", chain: str = None, **kwargs
    ) -> str:
        """
        List iptables rules with line numbers for a specific table and optional chain.

        Args:
            alias: Session alias for the connection.
            table: Table name (filter, nat, mangle, raw, security). Defaults to "filter".
            chain: Optional chain name (INPUT, OUTPUT, FORWARD, etc.).
            **kwargs: Additional command execution options.

        Returns:
            String containing rules with line numbers.
        """
        cmd = f"iptables -t {table} -L"
        if chain:
            cmd += f" {chain}"
        cmd += " -n -v --line-numbers"
        return self.execute_command(alias, cmd, **kwargs)

    def get_policy(self, alias: str, chain: str, table: str = "filter", **kwargs) -> str:
        """
        Get the default policy for a specific chain.

        Args:
            alias: Session alias for the connection.
            chain: Chain name (INPUT, OUTPUT, FORWARD, etc.).
            table: Table name (filter, nat, mangle, raw, security). Defaults to "filter".
            **kwargs: Additional command execution options.

        Returns:
            Policy value (ACCEPT, DROP, REJECT).
        """
        output = self.execute_command(
            alias, f"iptables -t {table} -L {chain} -n | head -1", **kwargs
        )
        # Parse output like: "Chain INPUT (policy DROP)"
        if "policy" in output:
            policy = output.split("policy")[1].strip().rstrip(")")
            return policy
        return output.strip()

    def list_chains(self, alias: str, table: str = "filter", **kwargs) -> List[str]:
        """
        List all chains in a specific table.

        Args:
            alias: Session alias for the connection.
            table: Table name (filter, nat, mangle, raw, security). Defaults to "filter".
            **kwargs: Additional command execution options.

        Returns:
            List of chain names.
        """
        output = self.execute_command(
            alias, f"iptables -t {table} -L -n | grep '^Chain' | awk '{{print $2}}'", **kwargs
        )
        return [line.strip() for line in output.strip().split("\n") if line.strip()]

    def count_rules(self, alias: str, chain: str, table: str = "filter", **kwargs) -> int:
        """
        Count the number of rules in a specific chain.

        Args:
            alias: Session alias for the connection.
            chain: Chain name (INPUT, OUTPUT, FORWARD, etc.).
            table: Table name (filter, nat, mangle, raw, security). Defaults to "filter".
            **kwargs: Additional command execution options.

        Returns:
            Number of rules in the chain.
        """
        output = self.execute_command(
            alias,
            f"iptables -t {table} -L {chain} -n --line-numbers | tail -n +3 | wc -l",
            **kwargs,
        )
        return int(output.strip())

    def rule_exists(
        self,
        alias: str,
        chain: str,
        rule_spec: str,
        table: str = "filter",
        **kwargs,
    ) -> bool:
        """
        Check if a specific rule exists in a chain.

        Args:
            alias: Session alias for the connection.
            chain: Chain name (INPUT, OUTPUT, FORWARD, etc.).
            rule_spec: Rule specification to check (e.g., "-s 192.168.1.0/24 -j ACCEPT").
            table: Table name (filter, nat, mangle, raw, security). Defaults to "filter".
            **kwargs: Additional command execution options.

        Returns:
            True if rule exists, False otherwise.
        """
        result = self.execute_command(
            alias,
            f"iptables -t {table} -C {chain} {rule_spec} 2>&1 ; echo $?",
            **kwargs,
        )
        return result.strip().endswith("0")

    def save_rules(self, alias: str, **kwargs) -> str:
        """
        Save current iptables rules using iptables-save.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            String containing saved rules in iptables-save format.
        """
        return self.execute_command(alias, "iptables-save", **kwargs)

    def list_by_spec(
        self, alias: str, table: str = "filter", chain: str = None, **kwargs
    ) -> str:
        """
        List iptables rules in specification format (as they would be entered).

        Args:
            alias: Session alias for the connection.
            table: Table name (filter, nat, mangle, raw, security). Defaults to "filter".
            chain: Optional chain name (INPUT, OUTPUT, FORWARD, etc.).
            **kwargs: Additional command execution options.

        Returns:
            String containing rules in specification format.
        """
        cmd = f"iptables -t {table} -S"
        if chain:
            cmd += f" {chain}"
        return self.execute_command(alias, cmd, **kwargs)
