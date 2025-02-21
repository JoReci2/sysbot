import unittest
from unittest.mock import patch, MagicMock
from sysbot.connectors.ConnectorHandler import ConnectorHandler
import json

class TestConnectorHandler(unittest.TestCase):

    def setUp(self):
        self.handler = ConnectorHandler()

    @patch('sysbot.connectors.ConnectorHandler.importlib.import_module')
    def test_get_protocol_success(self, mock_import_module):
        mock_protocol = MagicMock()
        mock_import_module.return_value = mock_protocol
        mock_protocol.someprotocol = MagicMock()
        
        self.handler.__get_protocol__('SomeProtocol')
        self.assertIsNotNone(self.handler.protocol)
        mock_import_module.assert_called_once_with('sysbot.connectors.someprotocol')
        self.assertTrue(hasattr(self.handler.protocol, 'someprotocol'))

    @patch('sysbot.connectors.ConnectorHandler.importlib.import_module')
    def test_get_protocol_failure(self, mock_import_module):
        mock_import_module.side_effect = ImportError
        with self.assertRaises(ValueError):
            self.handler.__get_protocol__('NonExistentProtocol')

    @patch('sysbot.connectors.ConnectorHandler.SSHTunnelForwarder')
    def test_nested_tunnel_success(self, mock_tunnel_forwarder):
        mock_tunnel = MagicMock()
        mock_tunnel.local_bind_port = 12345
        mock_tunnel_forwarder.return_value = mock_tunnel

        self.handler.protocol = MagicMock()
        self.handler.protocol.open_session.return_value = 'session'

        tunnel_config = [{'ip': '127.0.0.1', 'port': 22, 'username': 'user', 'password': 'pass'}]
        target_config = {'ip': '127.0.0.1', 'port': 80, 'username': 'user', 'password': 'pass'}

        result = self.handler.__nested_tunnel__(tunnel_config, target_config)
        self.assertEqual(result['session'], 'session')
        self.assertEqual(len(result['tunnels']), 1)
        mock_tunnel_forwarder.assert_called_once()

    @patch('sysbot.connectors.ConnectorHandler.SSHTunnelForwarder')
    def test_nested_tunnel_failure(self, mock_tunnel_forwarder):
        mock_tunnel_forwarder.side_effect = Exception("Tunnel error")
        tunnel_config = [{'ip': '127.0.0.1', 'port': 22, 'username': 'user', 'password': 'pass'}]
        target_config = {'ip': '127.0.0.1', 'port': 80, 'username': 'user', 'password': 'pass'}

        with self.assertRaises(Exception):
            self.handler.__nested_tunnel__(tunnel_config, target_config)

    @patch('sysbot.connectors.ConnectorHandler.ConnectorHandler.__nested_tunnel__')
    @patch('sysbot.connectors.ConnectorHandler.ConnectorHandler.__get_protocol__')
    def test_open_session_with_tunnel(self, mock_get_protocol, mock_nested_tunnel):
        mock_nested_tunnel.return_value = {'session': 'session', 'tunnels': ['tunnel']}
        self.handler.protocol = MagicMock()
        self.handler.protocol.open_session.return_value = 'session'

        tunnel_config = json.dumps([{'ip': '127.0.0.1', 'port': 22, 'username': 'user', 'password': 'pass'}])
        self.handler.open_session('alias', 'SomeProtocol', '127.0.0.1', 80, 'user', 'pass', tunnel_config)

        self.assertEqual(self.handler._cache._connections[0]['session'], 'session')
        self.assertEqual(self.handler._cache._connections[0]['tunnels'], ['tunnel'])

    @patch('sysbot.connectors.ConnectorHandler.ConnectorHandler.__get_protocol__')
    def test_open_session_without_tunnel(self, mock_get_protocol):
        self.handler.protocol = MagicMock()
        self.handler.protocol.open_session.return_value = 'session'

        self.handler.open_session('alias', 'SomeProtocol', '127.0.0.1', 80, 'user', 'pass')

        self.assertEqual(self.handler._cache._connections[0]['session'], 'session')
        self.assertIsNone(self.handler._cache._connections[0]['tunnels'])

    @patch('sysbot.connectors.ConnectorHandler.ConnectorHandler.__get_protocol__')
    def test_open_session_failure(self, mock_get_protocol):
        self.handler.protocol = MagicMock()
        self.handler.protocol.open_session.side_effect = Exception("Session error")

        with self.assertRaises(Exception):
            self.handler.open_session('alias', 'SomeProtocol', '127.0.0.1', 80, 'user', 'pass')

    @patch('sysbot.connectors.ConnectorHandler.ConnectorHandler.__get_protocol__')
    def test_execute_command_success(self, mock_get_protocol):
        self.handler.protocol = MagicMock()
        self.handler.protocol.execute_command.return_value = {'output': 'result'}
        self.handler._cache.register({'session': 'session'}, 'alias')

        result = self.handler.execute_command('alias', 'command')
        self.assertEqual(result, {'output': 'result'})

    @patch('sysbot.connectors.ConnectorHandler.ConnectorHandler.__get_protocol__')
    def test_execute_command_failure(self, mock_get_protocol):
        self.handler.protocol = MagicMock()
        self.handler._cache.register({'session': 'session'}, 'alias')

        self.handler.protocol.execute_command.side_effect = Exception("Command error")
        with self.assertRaises(Exception):
            self.handler.execute_command('alias', 'command')

    @patch('sysbot.connectors.ConnectorHandler.ConnectorHandler.__get_protocol__')
    def test_close_all_sessions(self, mock_get_protocol):
        self.handler.protocol = MagicMock()
        self.handler._cache.register({'session': 'session', 'tunnels': [MagicMock()]}, 'alias')

        self.handler.close_all_sessions()
        self.handler.protocol.close_session.assert_called_once_with('session')
        self.assertEqual(len(self.handler._cache._connections), 0)

if __name__ == '__main__':
    unittest.main()