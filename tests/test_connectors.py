"""
Unit tests for refactored connectors.
Tests basic functionality without requiring actual network connections.
"""

import unittest
from sysbot.connectors.config import DEFAULT_PORTS, create_response
from sysbot.connectors.localhost.bash import Bash as LocalhostBash


class TestConnectorConfig(unittest.TestCase):
    """Test connector configuration and utilities."""
    
    def test_default_ports(self):
        """Test default port definitions."""
        self.assertEqual(DEFAULT_PORTS["ssh"], 22)
        self.assertEqual(DEFAULT_PORTS["winrm"], 5986)
        self.assertEqual(DEFAULT_PORTS["http"], 80)
        self.assertEqual(DEFAULT_PORTS["https"], 443)
        self.assertIsNone(DEFAULT_PORTS["socket"])
    
    def test_create_response(self):
        """Test response format creation."""
        response = create_response(0, "test result", None, {"key": "value"})
        
        self.assertIn("StatusCode", response)
        self.assertIn("Result", response)
        self.assertIn("Error", response)
        self.assertIn("Metadata", response)
        
        self.assertEqual(response["StatusCode"], 0)
        self.assertEqual(response["Result"], "test result")
        self.assertIsNone(response["Error"])
        self.assertEqual(response["Metadata"]["key"], "value")
    
    def test_create_response_with_error(self):
        """Test error response creation."""
        response = create_response(1, None, "Test error", {})
        
        self.assertEqual(response["StatusCode"], 1)
        self.assertIsNone(response["Result"])
        self.assertEqual(response["Error"], "Test error")


class TestLocalhostConnector(unittest.TestCase):
    """Test localhost connector functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.connector = LocalhostBash()
    
    def test_open_session(self):
        """Test opening a localhost session."""
        session = self.connector.open_session()
        
        self.assertIsInstance(session, dict)
        self.assertIn("type", session)
        self.assertIn("os", session)
        self.assertIn("shell", session)
        self.assertEqual(session["type"], "localhost")
    
    def test_execute_command_success(self):
        """Test successful command execution."""
        session = self.connector.open_session()
        response = self.connector.execute_command(session, "echo test")
        
        self.assertIsInstance(response, dict)
        self.assertEqual(response["StatusCode"], 0)
        self.assertEqual(response["Result"], "test")
        self.assertIsNone(response["Error"])
        self.assertIn("Metadata", response)
    
    def test_execute_command_failure(self):
        """Test failed command execution."""
        session = self.connector.open_session()
        # Use a command that will fail
        response = self.connector.execute_command(session, "false")
        
        self.assertIsInstance(response, dict)
        self.assertNotEqual(response["StatusCode"], 0)
    
    def test_execute_command_with_output(self):
        """Test command with multi-line output."""
        session = self.connector.open_session()
        response = self.connector.execute_command(
            session, 
            "echo line1 && echo line2"
        )
        
        self.assertEqual(response["StatusCode"], 0)
        self.assertIn("line1", response["Result"])
        self.assertIn("line2", response["Result"])
    
    def test_close_session(self):
        """Test closing a session."""
        session = self.connector.open_session()
        # Should not raise any exception
        self.connector.close_session(session)


class TestSysbotIntegration(unittest.TestCase):
    """Test Sysbot integration with new connectors."""
    
    def test_import_sysbot(self):
        """Test that Sysbot can be imported."""
        from sysbot.Sysbot import Sysbot
        bot = Sysbot()
        self.assertIsNotNone(bot)
    
    def test_localhost_connection(self):
        """Test opening a localhost connection through Sysbot."""
        from sysbot.Sysbot import Sysbot
        
        bot = Sysbot()
        bot.open_session(
            alias="test_local",
            protocol="localhost",
            product="bash",
            host="localhost"
        )
        
        # Execute a simple command
        result = bot.execute_command("test_local", "echo Hello")
        self.assertEqual(result, "Hello")
        
        # Test full response
        full_response = bot.execute_command(
            "test_local", 
            "echo World", 
            get_full_response=True
        )
        self.assertIsInstance(full_response, dict)
        self.assertEqual(full_response["StatusCode"], 0)
        self.assertEqual(full_response["Result"], "World")
        
        bot.close_session("test_local")
    
    def test_default_port_handling(self):
        """Test that port parameter is optional."""
        from sysbot.Sysbot import Sysbot
        
        bot = Sysbot()
        # Should not raise an error with port=None
        bot.open_session(
            alias="test_local2",
            protocol="localhost",
            product="bash",
            host="localhost",
            port=None
        )
        
        result = bot.execute_command("test_local2", "echo Test")
        self.assertEqual(result, "Test")
        
        bot.close_session("test_local2")


if __name__ == "__main__":
    unittest.main()
