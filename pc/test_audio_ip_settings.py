import importlib.util
from pathlib import Path
import unittest
import socket
import struct
import tempfile
import threading

spec = importlib.util.spec_from_file_location('settings', Path(__file__).with_name('Audio-IP-Settings.py'))
settings = importlib.util.module_from_spec(spec)
spec.loader.exec_module(settings)

class SettingsTest(unittest.TestCase):
    def test_other_networks_and_whitespace(self):
        for ip in ('10.0.0.50', '172.16.8.12', '192.168.0.200', '192.168.1.254'):
            with self.subTest(ip=ip):
                self.assertEqual(settings.set_ip(b'', ' ' + ip + ' '), ('PC_IP=' + ip + '\n').encode())

    def test_unusable_destinations(self):
        for ip in ('', '::1', 'localhost', '0.0.0.0', '127.0.0.1', '224.0.0.1', '255.255.255.255', '192.168.1.999'):
            with self.subTest(ip=ip), self.assertRaises(ValueError):
                settings.set_ip(b'', ip)

    def test_duplicate_keys_bom_and_comment_bytes(self):
        old = b'\xef\xbb\xbf; caf\xe9\r\npc_ip=10.0.0.1\r\nPC_IP = 10.0.0.2\r\nOTHER=yes\r\n'
        self.assertEqual(settings.set_ip(old, '10.0.0.3'),
                         b'; caf\xe9\r\nPC_IP=10.0.0.3\r\nOTHER=yes\r\n')

    def test_update_retains_other_settings(self):
        old = b'; hello\r\nPC_IP=192.168.1.13\r\nOTHER=enabled\r\n'
        self.assertEqual(settings.set_ip(old, '192.168.1.88'),
                         b'; hello\r\nPC_IP=192.168.1.88\r\nOTHER=enabled\r\n')

    def test_create_and_reject_invalid_address(self):
        self.assertEqual(settings.set_ip(b'', '192.168.1.2'), b'PC_IP=192.168.1.2\n')
        with self.assertRaises(ValueError):
            settings.set_ip(b'', '192.168.1.256')

    def test_xbdm_update_and_verify(self):
        original = b'; old\r\nPC_IP=192.168.1.13\r\n'
        expected = b'; old\r\nPC_IP=192.168.1.44\r\n'
        with tempfile.TemporaryDirectory() as directory, socket.socket() as listener:
            settings.BACKUPS = Path(directory)
            listener.bind(('127.0.0.1', 0))
            listener.listen(1)
            errors = []
            def server():
                try:
                    conn, _ = listener.accept()
                    with conn:
                        f = conn.makefile('rwb', buffering=0)
                        f.write(b'201- connected\r\n')
                        self.assertTrue(f.readline().startswith(b'dirlist '))
                        f.write(b'202- listing\r\nname="PERFORMER-AV.ini"\r\n.\r\n')
                        self.assertTrue(f.readline().startswith(b'getfile '))
                        f.write(b'203- binary\r\n' + struct.pack('<I', len(original)) + original)
                        self.assertTrue(f.readline().startswith(b'sendfile '))
                        f.write(b'204- ready\r\n')
                        received = settings.read_exact(f, len(expected))
                        self.assertEqual(received, expected)
                        f.write(b'200- ok\r\n')
                        self.assertTrue(f.readline().startswith(b'getfile '))
                        f.write(b'203- binary\r\n' + struct.pack('<I', len(received)) + received)
                except BaseException as exc:
                    errors.append(exc)
            worker = threading.Thread(target=server, daemon=True)
            worker.start()
            settings.apply_config('127.0.0.1', '192.168.1.44', listener.getsockname()[1])
            worker.join(3)
            self.assertFalse(worker.is_alive())
            self.assertEqual(errors, [])
            self.assertEqual(next(Path(directory).iterdir()).read_bytes(), original)

if __name__ == '__main__':
    unittest.main()
