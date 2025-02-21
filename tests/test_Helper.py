import unittest
from sysbot.Helper import Helper
import re

class TestHelper(unittest.TestCase):
    def setUp(self):
        self.helper = Helper()

    def test_convert_timezone_to_offset_valid(self):
        # Test a valid timezone and ensure the returned offset is in the correct format (+/-HH:MM).
        offset = self.helper.convert_timezone_to_offset('America/New_York')
        self.assertTrue(re.match(r'^[\+\-]\d{2}:\d{2}$', offset))

    def test_convert_timezone_to_offset_unknown(self):
        # Test an invalid timezone and ensure UnknownTimeZoneError is raised.
        with self.assertRaises(Exception):
            self.helper.convert_timezone_to_offset('Invalid/Timezone')

if __name__ == '__main__':
    unittest.main()