"""
Iptables Module

This module provides methods for querying and managing iptables firewall rules
on Linux systems, including listing rules, checking chains, and viewing policies.
"""
from sysbot.utils.engine import ComponentBase
from typing import List, Dict
import re


class Iptables(ComponentBase):
    """Iptables firewall management class for Linux systems."""

    def list_rules(self, alias: str, table: str = "filter", **kwargs) -> Dict[str, List[Dict[str, str]]]:
        """
        List all iptables rules for a specific table.

        Args:
            alias: Session alias for the connection.
            table: Table name (filter, nat, mangle, raw, security). Defaults to "filter".
            **kwargs: Additional command execution options.

        Returns:
            Dictionary mapping chain names to lists of rule dictionaries.
            Each rule dictionary contains: num, pkts, bytes, target, prot, opt, in, out, source, destination.
        """
        output = self.execute_command(
            alias, f"iptables -t {table} -L -n -v --line-numbers", **kwargs
        )
        
        chains = {}
        current_chain = None
        
        for line in output.splitlines():
            line = line.strip()
            if not line:
                continue
            
            # Detect chain header: "Chain INPUT (policy ACCEPT)"
            if line.startswith("Chain "):
                parts = line.split()
                current_chain = parts[1]
                chains[current_chain] = []
            # Skip the column header line
            elif line.startswith("num ") or line.startswith("pkts "):
                continue
            # Parse rule lines
            elif current_chain and line[0].isdigit():
                parts = line.split(None, 10)  # Split into max 11 parts
                if len(parts) >= 9:
                    rule = {
                        "num": parts[0],
                        "pkts": parts[1],
                        "bytes": parts[2],
                        "target": parts[3],
                        "prot": parts[4],
                        "opt": parts[5],
                        "in": parts[6],
                        "out": parts[7],
                        "source": parts[8],
                        "destination": parts[9] if len(parts) > 9 else "",
                        "options": parts[10] if len(parts) > 10 else ""
                    }
                    chains[current_chain].append(rule)
        
        return chains

    def list_rules_line_numbers(
        self, alias: str, table: str = "filter", chain: str = None, **kwargs
    ) -> Dict[str, List[Dict[str, str]]]:
        """
        List iptables rules with line numbers for a specific table and optional chain.

        Args:
            alias: Session alias for the connection.
            table: Table name (filter, nat, mangle, raw, security). Defaults to "filter".
            chain: Optional chain name (INPUT, OUTPUT, FORWARD, etc.).
            **kwargs: Additional command execution options.

        Returns:
            Dictionary mapping chain names to lists of rule dictionaries.
            Each rule dictionary contains: num, pkts, bytes, target, prot, opt, in, out, source, destination.
        """
        cmd = f"iptables -t {table} -L"
        if chain:
            cmd += f" {chain}"
        cmd += " -n -v --line-numbers"
        output = self.execute_command(alias, cmd, **kwargs)
        
        chains = {}
        current_chain = None
        
        for line in output.splitlines():
            line = line.strip()
            if not line:
                continue
            
            # Detect chain header
            if line.startswith("Chain "):
                parts = line.split()
                current_chain = parts[1]
                chains[current_chain] = []
            # Skip the column header line
            elif line.startswith("num ") or line.startswith("pkts "):
                continue
            # Parse rule lines
            elif current_chain and line[0].isdigit():
                parts = line.split(None, 10)
                if len(parts) >= 9:
                    rule = {
                        "num": parts[0],
                        "pkts": parts[1],
                        "bytes": parts[2],
                        "target": parts[3],
                        "prot": parts[4],
                        "opt": parts[5],
                        "in": parts[6],
                        "out": parts[7],
                        "source": parts[8],
                        "destination": parts[9] if len(parts) > 9 else "",
                        "options": parts[10] if len(parts) > 10 else ""
                    }
                    chains[current_chain].append(rule)
        
        return chains

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
        match = re.search(r'policy\s+(\w+)', output)
        if match:
            return match.group(1)
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
        # Get the last line which contains the exit code
        exit_code = result.strip().split('\n')[-1]
        return exit_code == "0"

    def save_rules(self, alias: str, **kwargs) -> Dict[str, List[str]]:
        """
        Save current iptables rules using iptables-save.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary mapping table names to lists of rule specifications.
        """
        output = self.execute_command(alias, "iptables-save", **kwargs)
        
        tables = {}
        current_table = None
        
        for line in output.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            
            # Detect table: "*filter", "*nat", etc.
            if line.startswith("*"):
                current_table = line[1:]  # Remove the asterisk
                tables[current_table] = []
            # Skip COMMIT lines
            elif line == "COMMIT":
                continue
            # Add rule/chain lines to current table
            elif current_table:
                tables[current_table].append(line)
        
        return tables

    def list_by_spec(
        self, alias: str, table: str = "filter", chain: str = None, **kwargs
    ) -> List[str]:
        """
        List iptables rules in specification format (as they would be entered).

        Args:
            alias: Session alias for the connection.
            table: Table name (filter, nat, mangle, raw, security). Defaults to "filter".
            chain: Optional chain name (INPUT, OUTPUT, FORWARD, etc.).
            **kwargs: Additional command execution options.

        Returns:
            List of rule specification strings.
        """
        cmd = f"iptables -t {table} -S"
        if chain:
            cmd += f" {chain}"
        output = self.execute_command(alias, cmd, **kwargs)
        return [line.strip() for line in output.splitlines() if line.strip()]
