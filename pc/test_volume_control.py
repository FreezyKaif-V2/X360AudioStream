import importlib.util
import io
import sys
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('receiver', Path(__file__).with_name('PC-Audio-Receiver.py'))
receiver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(receiver)

class VolumeControlTest(unittest.TestCase):
    def test_live_volume_changes_ignore_invalid_values(self):
        original = sys.stdin
        try:
            sys.stdin = io.StringIO('200\ninvalid\n301\n175\n')
            receiver.volume_gain = 1.0
            receiver.volume_control_thread()
            self.assertEqual(receiver.volume_gain, 1.75)
        finally:
            sys.stdin = original

if __name__ == '__main__':
    unittest.main()
