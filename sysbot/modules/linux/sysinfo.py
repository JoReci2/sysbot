from sysbot.utils.engine import ComponentBase


class Sysinfo(ComponentBase):
    def os_release(self, alias):
        output = self.execute_command(alias, "cat /etc/os-release")
        data = {}
        for line in output.splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                if "=" in line:
                    key, value = line.split("=", 1)
                    data[key] = value.strip("\"'")
        return data

    def hostname(self, alias: str) -> str:
        return self.execute_command(alias, "hostname -s")

    def fqdn(self, alias: str) -> str:
        return self.execute_command(alias, "hostname -f")

    def domain(self, alias: str) -> str:
        return self.execute_command(alias, "hostname -d")

    def uptime(self, alias: str) -> str:
        return self.execute_command(alias, "uptime --pretty")

    def kernel(self, alias: str) -> str:
        return self.execute_command(alias, "uname -r")

    def architecture(self, alias: str) -> str:
        return self.execute_command(alias, "uname -m")

    def ram(self, alias: str) -> dict:
        output = self.execute_command(alias, "free -h")
        lines = output.splitlines()
        if len(lines) >= 2:
            headers = lines[0].split()
            values = lines[1].split()
            return dict(zip(headers, values))
        return {}

    def cpu(self, alias: str) -> dict:
        output = self.execute_command(alias, "lscpu")
        lines = output.splitlines()
        cpu_info = {}
        for line in lines:
            if ":" in line:
                key, value = line.split(":", 1)
                cpu_info[key.strip()] = value.strip()
        return cpu_info

    def keyboard(self, alias: str) -> str:
        return self.execute_command(
            alias, "localectl | grep Keymap | awk '{print $3}' | tr -d ' '"
        )

    def timezone(self, alias: str) -> str:
        return self.execute_command(
            alias, "timedatectl | grep 'Time zone' | awk '{print $3}' | tr -d ' '"
        )

    def env(self, alias: str) -> dict:
        output = self.execute_command(alias, "printenv")
        env_vars = {}
        for line in output.splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                env_vars[key] = value.strip()
        return env_vars

    def process(self, alias: str) -> dict:
        output = self.execute_command(alias, "ps -Aww -o pid,user,comm,pcpu,pmem")
        processes = {}
        for line in output.splitlines()[1:]:
            if line:
                pid, user, comm, pcpu, pmem = line.split(None, 4)
                processes[pid] = {
                    "user": user,
                    "command": comm,
                    "cpu": pcpu,
                    "memory": pmem
                }
        return processes