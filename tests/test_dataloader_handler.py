import unittest
from unittest.mock import patch, MagicMock
from sysbot.dataloaders.DataloaderHandler import DataloaderHandler

class TestDataloaderHandler(unittest.TestCase):
    def setUp(self):
        self.handler = DataloaderHandler()

    @patch("importlib.import_module")
    def test_import_data_from_calls_load(self, mock_import):
        fake_module = MagicMock()
        fake_module.load.return_value = {"test": "data"}
        mock_import.return_value = fake_module

        result = self.handler.import_data_from("SomeModule", key="value")
        self.assertEqual(result, {"test": "data"})
        fake_module.load.assert_called_once_with(key="value")

    @patch("importlib.import_module", side_effect=ModuleNotFoundError())
    def test_import_data_from_module_not_found(self, mock_import):
        with self.assertRaises(ValueError) as context:
            self.handler.import_data_from("Unknown")
        self.assertIn("No loader available for module: unknown", str(context.exception))

    @patch("importlib.import_module", side_effect=Exception("generic error"))
    def test_import_data_from_generic_error(self, mock_import):
        with self.assertRaises(RuntimeError) as context:
            self.handler.import_data_from("AnyModule")
        self.assertIn("An error occurred while processing the module: generic error", str(context.exception))

if __name__ == '__main__':
    unittest.main()