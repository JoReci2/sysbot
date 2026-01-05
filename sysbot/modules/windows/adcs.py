"""
Active Directory Certificate Services Module

This module provides methods for managing and querying Active Directory Certificate
Services (AD CS) including Certificate Authorities, issued certificates, templates,
and PKI operations using PowerShell ADCS cmdlets.
"""
from sysbot.utils.engine import ComponentBase
import json


class Adcs(ComponentBase):
    """Active Directory Certificate Services management class using PowerShell ADCS cmdlets."""

    def get_ca(self, alias: str, **kwargs) -> dict:
        """
        Get Certificate Authority information.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing CA information including Name, Type, ConfigString, and Certificate.
        """
        command = "Get-CertificationAuthority | Select-Object Name, Type, ConfigString, Certificate | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        if not output or output.strip() == "":
            return {}
        return json.loads(output)

    def get_ca_property(self, alias: str, **kwargs) -> dict:
        """Get Certificate Authority properties."""
        command = "Get-CAProperty | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        if not output or output.strip() == "":
            return {}
        return json.loads(output)

    def get_issued_certificates(self, alias: str, **kwargs) -> list:
        """Get issued certificates."""
        command = "Get-IssuedRequest | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        if not output or output.strip() == "":
            return []
        result = json.loads(output)
        # Wrap single objects in a list
        if isinstance(result, dict):
            return [result]
        return result

    def get_pending_requests(self, alias: str, **kwargs) -> list:
        """Get pending certificate requests."""
        command = "Get-PendingRequest | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        if not output or output.strip() == "":
            return []
        result = json.loads(output)
        # Wrap single objects in a list
        if isinstance(result, dict):
            return [result]
        return result

    def get_failed_requests(self, alias: str, **kwargs) -> list:
        """Get failed certificate requests."""
        command = "Get-FailedRequest | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        if not output or output.strip() == "":
            return []
        result = json.loads(output)
        # Wrap single objects in a list
        if isinstance(result, dict):
            return [result]
        return result

    def get_certificate_templates(self, alias: str, **kwargs) -> list:
        """Get certificate templates."""
        command = "Get-CATemplate | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        if not output or output.strip() == "":
            return []
        result = json.loads(output)
        # Wrap single objects in a list
        if isinstance(result, dict):
            return [result]
        return result

    def get_crl(self, alias: str, **kwargs) -> dict:
        """Get Certificate Revocation List information."""
        command = "Get-CACrlDistributionPoint | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        if not output or output.strip() == "":
            return {}
        return json.loads(output)

    def get_certificate(self, alias: str, request_id: int, **kwargs) -> dict:
        """Get specific certificate by request ID."""
        command = f"Get-IssuedRequest -RequestId {request_id} | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        if not output or output.strip() == "":
            return {}
        return json.loads(output)

    def get_revoked_certificates(self, alias: str, **kwargs) -> list:
        """Get revoked certificates."""
        command = "Get-RevokedRequest | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        if not output or output.strip() == "":
            return []
        result = json.loads(output)
        # Wrap single objects in a list
        if isinstance(result, dict):
            return [result]
        return result
