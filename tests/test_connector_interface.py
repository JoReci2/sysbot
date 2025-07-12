import unittest
from sysbot.connectors.ConnectorInterface import ConnectorInterface
from sysbot.connectors.ssh.bash import Bash
from sysbot.connectors.http.basicauth import Basicauth
from sysbot.connectors.winrm.powershell import Powershell


class TestConnectorInterface(unittest.TestCase):

    def test_bash_inherits_from_connector_interface(self):
        """Test that Bash connector inherits from ConnectorInterface"""
        bash = Bash()
        self.assertIsInstance(bash, ConnectorInterface)

    def test_basicauth_inherits_from_connector_interface(self):
        """Test that Basicauth connector inherits from ConnectorInterface"""
        basicauth = Basicauth()
        self.assertIsInstance(basicauth, ConnectorInterface)

    def test_powershell_inherits_from_connector_interface(self):
        """Test that Powershell connector inherits from ConnectorInterface"""
        powershell = Powershell()
        self.assertIsInstance(powershell, ConnectorInterface)

    def test_connector_interface_cannot_be_instantiated(self):
        """Test that ConnectorInterface cannot be instantiated directly"""
        with self.assertRaises(TypeError):
            ConnectorInterface()

    def test_all_connectors_have_required_methods(self):
        """Test that all connectors implement required methods"""
        connectors = [Bash(), Basicauth(), Powershell()]
        
        for connector in connectors:
            self.assertTrue(hasattr(connector, 'open_session'))
            self.assertTrue(hasattr(connector, 'execute_command'))
            self.assertTrue(hasattr(connector, 'close_session'))
            
            # Verify methods are callable
            self.assertTrue(callable(getattr(connector, 'open_session')))
            self.assertTrue(callable(getattr(connector, 'execute_command')))
            self.assertTrue(callable(getattr(connector, 'close_session')))


class InvalidConnector(ConnectorInterface):
    """Invalid connector that doesn't implement all required methods"""
    def open_session(self, host, port, login, password):
        pass
    # Missing execute_command and close_session


class TestInvalidConnector(unittest.TestCase):
    
    def test_invalid_connector_cannot_be_instantiated(self):
        """Test that a connector missing required methods cannot be instantiated"""
        with self.assertRaises(TypeError):
            InvalidConnector()


if __name__ == '__main__':
    unittest.main()