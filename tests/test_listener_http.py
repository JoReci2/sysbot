import unittest
from unittest.mock import patch, mock_open, MagicMock
from sysbot.listeners.http import Listener

class TestListener(unittest.TestCase):
    def test_init_with_valid_config(self):
        config_content = """project:
  name: test
  version: 0.0.1
server:
  url: http://localhost:5000/api/v1/test_results
  login: admin
  password: admin
"""
        with patch("builtins.open", mock_open(read_data=config_content)):
            listener = Listener("dummy.yml")
            self.assertEqual(listener.config["project"]["name"], "test")
            self.assertEqual(listener.config["server"]["url"], "http://localhost:5000/api/v1/test_results")

    def test_init_with_invalid_config(self):
        invalid_configs = [
            "invalid: config",  # Manque les sections 'project' et 'server'
            "project:\n  name: test",  # Incomplet, il manque 'version' et 'server'
            "server:\n  url: http://localhost",  # Incomplet, il manque 'project'
            "project:\n  name: test\n  version: 0.0.1\nserver: {}",  # 'server' est vide
        ]

        for invalid_config in invalid_configs:
            with self.subTest(config=invalid_config):
                with patch("builtins.open", mock_open(read_data=invalid_config)):
                    with self.assertRaises(Exception):  # Doit lever une exception
                        Listener("dummy.yml")

    @patch("requests.post")
    def test_end_test(self, mock_post):
        config_content = """project:
  name: test
  version: 0.0.1
server:
  url: http://localhost:5000/api/v1/test_results
  login: admin
  password: admin
"""
        with patch("builtins.open", mock_open(read_data=config_content)):
            listener = Listener("dummy.yml")
            mock_attributes = MagicMock()
            mock_attributes.name = "ExampleTest"
            mock_attributes.status = "PASS"
            mock_attributes.message = "All good"
            mock_attributes.tags = ["tag1", "tag2"]

            mock_suite_attributes = MagicMock()
            mock_suite_attributes.name = "ExampleSuite"
            mock_suite_attributes.source = "SuiteSource"
            mock_suite_attributes.tags = ["suiteTag"]
            listener.start_suite("ExampleSuite", mock_suite_attributes)
            listener.end_test("ExampleTest", mock_attributes)

            mock_post.assert_called_once()
            call_args = mock_post.call_args[1]
            self.assertEqual(call_args["url"], "http://localhost:5000/api/v1/test_results")
            self.assertEqual(call_args["json"]["test_case_name"], "ExampleTest")

if __name__ == "__main__":
    unittest.main()