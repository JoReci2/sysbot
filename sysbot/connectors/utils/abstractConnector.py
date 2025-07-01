from abc import ABC, abstractmethod

class AbstractConnector(ABC):
    """
    Abstract base class for protocol-specific connectors.
    """

    @abstractmethod
    def open_session(self, host: str, port: int, login: str = None, password: str = None) -> object:
        """
        Open a session to the target host.
        """
        pass

    @abstractmethod
    def execute_command(self, session: object, command: str, script: bool = False, runas: bool = False) -> any:
        """
        Execute a command on the specified session.
        """
        pass

    @abstractmethod
    def close_session(self, session: object) -> None:
        """
        Close the specified session.
        """
        pass