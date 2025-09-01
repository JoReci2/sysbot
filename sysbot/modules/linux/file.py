from sysbot.utils.engine import ComponentBase


class File(ComponentBase):
    def is_present(self, alias: str, path: str, **kwargs) -> bool:
        return self.execute_command(alias, f"test -e {path} ; echo $?", **kwargs) == "0"

    def is_file(self, alias: str, path: str, **kwargs) -> bool:
        return self.execute_command(alias, f"test -f {path} ; echo $?", **kwargs) == "0"

    def is_directory(self, alias: str, path: str, **kwargs) -> bool:
        return self.execute_command(alias, f"test -d {path} ; echo $?", **kwargs) == "0"

    def is_executable(self, alias: str, path: str, **kwargs) -> bool:
        return self.execute_command(alias, f"test -x {path} ; echo $?", **kwargs) == "0"

    def is_pipe(self, alias: str, path: str, **kwargs) -> bool:
        return self.execute_command(alias, f"test -p {path} ; echo $?", **kwargs) == "0"

    def is_socket(self, alias: str, path: str, **kwargs) -> bool:
        return self.execute_command(alias, f"test -S {path} ; echo $?", **kwargs) == "0"

    def is_symlink(self, alias: str, path: str, **kwargs) -> bool:
        return self.execute_command(alias, f"test -L {path} ; echo $?", **kwargs) == "0"

    def realpath(self, alias: str, path: str, **kwargs) -> str:
        return self.execute_command(alias, f"realpath {path}", **kwargs)

    def user(self, alias: str, path: str, **kwargs) -> str:
        return self.execute_command(alias, f"stat -Lc %U {path}", **kwargs)

    def uid(self, alias: str, path: str, **kwargs) -> str:
        return self.execute_command(alias, f"stat -Lc %u {path}", **kwargs)

    def group(self, alias: str, path: str, **kwargs) -> str:
        return self.execute_command(alias, f"stat -Lc %G {path}", **kwargs)

    def gid(self, alias: str, path: str, **kwargs) -> str:
        return self.execute_command(alias, f"stat -Lc %g {path}", **kwargs)

    def mode(self, alias: str, path: str, **kwargs) -> str:
        return self.execute_command(alias, f"stat -Lc %a {path}", **kwargs)

    def size(self, alias: str, path: str, **kwargs) -> str:
        return self.execute_command(alias, f"stat -Lc %s {path}", **kwargs)

    def md5sum(self, alias: str, path: str, **kwargs) -> str:
        return self.execute_command(alias, f"md5sum {path} | cut -d' ' -f1", **kwargs)

    def content(self, alias: str, path: str, **kwargs) -> str:
        return self.execute_command(alias, f"cat {path}", **kwargs)

    def contains(self, alias: str, path: str, pattern: str, **kwargs) -> bool:
        return (
            self.execute_command(
                alias, f"grep -qs -- {pattern} {path} ; echo $?", **kwargs
            )
            == "0"
        )
