"""
Podman Container Module

This module provides methods for managing Podman containers and pods on Linux
systems, including container lifecycle operations, inspections, and resource
management.
"""
from sysbot.utils.engine import ComponentBase
import json


class Podman(ComponentBase):
    def version(self, alias: str, **kwargs) -> dict:
        output = self.execute_command(alias, "podman version --format json", **kwargs)
        return json.loads(output)

    def configuration(self, alias: str, **kwargs) -> dict:
        output = self.execute_command(alias, "podman info --format json", **kwargs)
        return json.loads(output)

    def containers(self, alias: str, **kwargs) -> dict:
        output = self.execute_command(
            alias, "podman container ls -a --format json", **kwargs
        )
        return json.loads(output)

    def container_inspect(self, alias: str, name: str, **kwargs) -> dict:
        output = self.execute_command(
            alias, f"podman container inspect {name} --format json", **kwargs
        )
        return json.loads(output)

    def pods(self, alias: str, **kwargs) -> dict:
        output = self.execute_command(alias, "podman pod ls --format json", **kwargs)
        return json.loads(output)

    def pod_inspect(self, alias: str, name: str, **kwargs) -> dict:
        output = self.execute_command(
            alias, f"podman pod inspect {name} --format json", **kwargs
        )
        return json.loads(output)

    def volumes(self, alias: str, **kwargs) -> dict:
        output = self.execute_command(alias, "podman volume ls --format json", **kwargs)
        return json.loads(output)

    def volume_inspect(self, alias: str, name: str, **kwargs) -> dict:
        output = self.execute_command(
            alias, f"podman volume inspect {name} --format json", **kwargs
        )
        return json.loads(output)

    def images(self, alias: str, **kwargs) -> dict:
        output = self.execute_command(alias, "podman image ls --format json", **kwargs)
        return json.loads(output)

    def image_inspect(self, alias: str, name: str, **kwargs) -> dict:
        output = self.execute_command(
            alias, f"podman image inspect {name} --format json", **kwargs
        )
        return json.loads(output)
