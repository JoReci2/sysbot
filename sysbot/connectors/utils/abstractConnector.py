from abc import ABC, abstractmethod
from typing import Optional

class AbstractConnector(ABC):
    """
    Abstract base class for protocol-specific connectors. All connectors must inherit from cette classe et implémenter les méthodes requises. Les paramètres login et password peuvent être None, les implémentations doivent gérer ce cas.
    """

    @abstractmethod
    def open_session(self, host: str, port: int, login: Optional[str] = None, password: Optional[str] = None) -> object:
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