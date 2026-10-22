"""Mock transport tests: no device or pyserial installation required."""
import importlib.util
import sys
import types
import unittest
from unittest.mock import Mock, patch

from tests._paths import ROOT


def load_tool():
    serial = types.ModuleType("serial")
    serial.tools = types.ModuleType("serial.tools")
    serial.tools.list_ports = types.ModuleType("serial.tools.list_ports")
    spec = importlib.util.spec_from_file_location("usb_tool_test", ROOT / "tools/quadzilla_tool.py")
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, {"serial": serial, "serial.tools": serial.tools,
                                 "serial.tools.list_ports": serial.tools.list_ports}):
        spec.loader.exec_module(module)
    return module


class UsbResponses(unittest.TestCase):
    def setUp(self):
        self.conn = load_tool().QuadzillaConnection()
        self.conn.serial = Mock(timeout=5.0)

    def test_read_error_restores_timeout(self):
        self.conn.serial.read.side_effect = OSError("disconnected")
        with self.assertRaises(OSError):
            self.conn.recv_raw(8, timeout=0)
        self.assertEqual(self.conn.serial.timeout, 5.0)

    def test_truncated_features_cannot_look_like_success(self):
        self.conn.serial.read.side_effect = [bytes([0x11, 2]), bytes(9)]
        with self.assertRaisesRegex(ConnectionError, "truncated"):
            self.conn.read_feature_codes()

    def test_module_info_preserves_raw_data_without_guessing_fields(self):
        response = bytes(range(25))
        self.conn.serial.read.return_value = response
        result = self.conn.get_module_info()
        self.assertEqual(result, {"raw": response.hex(), "response_code": 0, "data": response[1:].hex()})


if __name__ == "__main__":
    unittest.main()
