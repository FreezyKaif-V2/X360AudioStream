"""Check that a waiting replacement connection releases an idle old socket."""
import importlib.util
from pathlib import Path
import socket
import threading
import unittest

spec = importlib.util.spec_from_file_location('receiver', Path(__file__).with_name('PC-Audio-Receiver.py'))
receiver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(receiver)

class ReconnectTest(unittest.TestCase):
    def test_idle_connection_yields_to_new_connection(self):
        with socket.socket() as listener:
            listener.bind(('127.0.0.1', 0))
            listener.listen(2)
            receiver.server_sock = listener
            with socket.create_connection(listener.getsockname()) as first:
                old, _ = listener.accept()
                with old:
                    outcome = []
                    def reader():
                        try:
                            receiver.recv_exact(old, receiver.HEADER_SIZE)
                        except ConnectionResetError:
                            outcome.append('replace')
                    thread = threading.Thread(target=reader, daemon=True)
                    thread.start()
                    with socket.create_connection(listener.getsockname()):
                        thread.join(3)
                    self.assertFalse(thread.is_alive())
                    self.assertEqual(outcome, ['replace'])

if __name__ == '__main__':
    unittest.main()
