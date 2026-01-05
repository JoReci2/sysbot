"""
Podman Container Module

This module provides methods for managing Podman containers and pods on Linux
systems, including container lifecycle operations, inspections, and resource
management.
"""
from sysbot.utils.engine import ComponentBase
import json


class Podman(ComponentBase):
    """Podman container management class for Linux systems."""

    def version(self, alias: str, **kwargs) -> dict:
        """
        Get Podman version information.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing Podman version information in JSON format.
        """
        output = self.execute_command(alias, "podman version --format json", **kwargs)
        return json.loads(output)

    def configuration(self, alias: str, **kwargs) -> dict:
        """
        Get Podman system configuration and information.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing Podman system information in JSON format.
        """
        output = self.execute_command(alias, "podman info --format json", **kwargs)
        return json.loads(output)

    def containers(self, alias: str, **kwargs) -> dict:
        """
        List all containers (running and stopped).

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing all containers in JSON format.
        """
        output = self.execute_command(
            alias, "podman container ls -a --format json", **kwargs
        )
        return json.loads(output)

    def container_inspect(self, alias: str, name: str, **kwargs) -> dict:
        """
        Get detailed information about a specific container.

        Args:
            alias: Session alias for the connection.
            name: Container name or ID.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing container details in JSON format.
        """
        output = self.execute_command(
            alias, f"podman container inspect {name} --format json", **kwargs
        )
        return json.loads(output)

    def pods(self, alias: str, **kwargs) -> dict:
        """
        List all pods.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing all pods in JSON format.
        """
        output = self.execute_command(alias, "podman pod ls --format json", **kwargs)
        return json.loads(output)

    def pod_inspect(self, alias: str, name: str, **kwargs) -> dict:
        """
        Get detailed information about a specific pod.

        Args:
            alias: Session alias for the connection.
            name: Pod name or ID.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing pod details in JSON format.
        """
        output = self.execute_command(
            alias, f"podman pod inspect {name} --format json", **kwargs
        )
        return json.loads(output)

    def volumes(self, alias: str, **kwargs) -> dict:
        """
        List all volumes.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing all volumes in JSON format.
        """
        output = self.execute_command(alias, "podman volume ls --format json", **kwargs)
        return json.loads(output)

    def volume_inspect(self, alias: str, name: str, **kwargs) -> dict:
        """
        Get detailed information about a specific volume.

        Args:
            alias: Session alias for the connection.
            name: Volume name.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing volume details in JSON format.
        """
        output = self.execute_command(
            alias, f"podman volume inspect {name} --format json", **kwargs
        )
        return json.loads(output)

    def images(self, alias: str, **kwargs) -> dict:
        """
        List all images.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing all images in JSON format.
        """
        output = self.execute_command(alias, "podman image ls --format json", **kwargs)
        return json.loads(output)

    def image_inspect(self, alias: str, name: str, **kwargs) -> dict:
        """
        Get detailed information about a specific image.

        Args:
            alias: Session alias for the connection.
            name: Image name or ID.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing image details in JSON format.
        """
        output = self.execute_command(
            alias, f"podman image inspect {name} --format json", **kwargs
        )
        return json.loads(output)
