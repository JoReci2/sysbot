from sysbot.utils.engine import ComponentBase
import shlex


class Libvirt(ComponentBase):
    def list(self, alias: str, **kwargs) -> list:
        output = self.execute_command(alias, "virsh list --all --name", **kwargs)
        domains = [line.strip() for line in output.strip().split("\n") if line.strip()]
        return domains

    def dominfo(self, alias: str, domain: str, **kwargs) -> dict:
        output = self.execute_command(
            alias, f"virsh dominfo {shlex.quote(domain)}", **kwargs
        )
        info = {}
        for line in output.strip().split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                info[key.strip()] = value.strip()
        return info

    def domstate(self, alias: str, domain: str, **kwargs) -> str:
        output = self.execute_command(
            alias, f"virsh domstate {shlex.quote(domain)}", **kwargs
        )
        return output.strip()

    def pool_list(self, alias: str, **kwargs) -> list:
        output = self.execute_command(alias, "virsh pool-list --all --name", **kwargs)
        pools = [line.strip() for line in output.strip().split("\n") if line.strip()]
        return pools

    def pool_info(self, alias: str, pool: str, **kwargs) -> dict:
        output = self.execute_command(
            alias, f"virsh pool-info {shlex.quote(pool)}", **kwargs
        )
        info = {}
        for line in output.strip().split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                info[key.strip()] = value.strip()
        return info

    def net_list(self, alias: str, **kwargs) -> list:
        output = self.execute_command(alias, "virsh net-list --all --name", **kwargs)
        networks = [
            line.strip() for line in output.strip().split("\n") if line.strip()
        ]
        return networks

    def net_info(self, alias: str, network: str, **kwargs) -> dict:
        output = self.execute_command(
            alias, f"virsh net-info {shlex.quote(network)}", **kwargs
        )
        info = {}
        for line in output.strip().split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                info[key.strip()] = value.strip()
        return info

    def version(self, alias: str, **kwargs) -> dict:
        output = self.execute_command(alias, "virsh version", **kwargs)
        info = {}
        for line in output.strip().split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                info[key.strip()] = value.strip()
        return info

    def nodeinfo(self, alias: str, **kwargs) -> dict:
        output = self.execute_command(alias, "virsh nodeinfo", **kwargs)
        info = {}
        for line in output.strip().split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                info[key.strip()] = value.strip()
        return info
