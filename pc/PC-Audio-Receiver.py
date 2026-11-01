#!/usr/bin/env python3
"""
PC-Audio-Receiver.py
Low-latency 48 kHz 16-bit stereo PCM audio stream receiver for Xbox 360.
Works with Xbox360Audio.xex
"""

import socket
import struct
import time
import threading
import queue
import sys
import math
import signal
import os
import select
import argparse

try:
    import sounddevice as sd
    import numpy as np
    HAVE_AUDIO = True
except ImportError:
    HAVE_AUDIO = False

PORT = 36000
MAGIC = 0x48593337  # 'HY37'
HEADER_FMT = ">IBBHHHIIII"
HEADER_SIZE = struct.calcsize(HEADER_FMT)

BUFFER_FRAMES = 4
audio_queue = queue.Queue(maxsize=BUFFER_FRAMES)
stop_event = threading.Event()
volume_gain = 1.0
output_device = None
output_latency = 'low'

current_client_sock = None
server_sock = None

def signal_handler(signum, frame):
    stop_event.set()
    global current_client_sock, server_sock
    if current_client_sock:
        try:
            current_client_sock.close()
        except Exception:
            pass
    if server_sock:
        try:
            server_sock.close()
        except Exception:
            pass
    print("\n[*] Gracefully stopping audio receiver...")
    os._exit(0)

signal.signal(signal.SIGINT, signal_handler)
if hasattr(signal, "SIGBREAK"):
    signal.signal(signal.SIGBREAK, signal_handler)

def recv_exact(sock, n):
    buf = bytearray()
    while len(buf) < n and not stop_event.is_set():
        try:
            # A title transition can leave the old console socket open while
            # its replacement is already waiting in the listen backlog.
            # Abandon a partial packet with the old socket; main() accepts the
            # pending connection on its next iteration.
            readable, _, _ = select.select([sock, server_sock], [], [], 0.5)
            if server_sock in readable:
                raise ConnectionResetError('A newer Xbox connection is waiting')
            if sock not in readable:
                continue
            chunk = sock.recv(n - len(buf))
            if not chunk:
                raise ConnectionResetError("Connection closed by Xbox")
            buf.extend(chunk)
        except socket.timeout:
            continue
    if stop_event.is_set():
        raise KeyboardInterrupt
    return bytes(buf)

def audio_player_thread():
    if not HAVE_AUDIO:
        print("[!] sounddevice not installed. Audio output disabled.")
        return

    current_rate = 48000
    current_channels = 2
    stream = None

    try:
        stream = sd.RawOutputStream(
            samplerate=current_rate,
            channels=current_channels,
            dtype='int16',
            blocksize=0,
            latency=output_latency,
            device=output_device,
        )
        stream.start()
        print(f"[*] Audio engine active: {current_rate} Hz, {current_channels}ch, 16-bit PCM (RawOutputStream)")
        print(f"[*] Audio device output latency: {float(stream.latency) * 1000:.1f} ms (device-reported only)")

        while not stop_event.is_set():
            try:
                raw_chunk = audio_queue.get(timeout=0.1)
            except queue.Empty:
                continue

            if volume_gain != 1.0:
                try:
                    arr = np.frombuffer(raw_chunk, dtype=np.int16).astype(np.float32)
                    arr = np.clip(arr * volume_gain, -32768, 32767).astype(np.int16)
                    stream.write(arr.tobytes())
                except Exception:
                    stream.write(raw_chunk)
            else:
                stream.write(raw_chunk)

    except Exception as e:
        if not stop_event.is_set():
            print(f"\n[!] Audio stream error: {e}")
    finally:
        if stream:
            try:
                stream.stop()
                stream.close()
            except Exception:
                pass

def compute_db(payload):
    try:
        samples = np.frombuffer(payload, dtype=np.int16)
        if len(samples) == 0:
            return -96.0
        rms = np.sqrt(np.mean(samples.astype(np.float32) ** 2))
        if rms < 1.0:
            return -96.0
        return 20.0 * math.log10(rms / 32768.0)
    except Exception:
        return -96.0

def volume_control_thread():
    """Accept volume changes from the control window while playback runs."""
    global volume_gain
    for line in sys.stdin:
        try:
            value = float(line.strip())
            if 0 <= value <= 300:
                volume_gain = value / 100.0
                print(f'\n[volume] Applied {value:g}%', flush=True)
        except ValueError:
            continue

def main():
    global current_client_sock, server_sock
    global volume_gain, output_device, output_latency
    parser = argparse.ArgumentParser(description='Play the Xbox audio stream on this PC.')
    parser.add_argument('--volume', type=float, default=200, metavar='PERCENT',
                        help='Output volume in percent (default: 200; values above 100 can clip).')
    parser.add_argument('--device', help='Output device name or numeric ID (default: system default).')
    parser.add_argument('--latency-ms', type=float, help='Requested output latency in milliseconds (default: audio device low setting).')
    parser.add_argument('--list-devices', action='store_true', help='List audio devices and exit.')
    parser.add_argument('--volume-control-stdin', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.list_devices:
        if not HAVE_AUDIO:
            parser.error('Install sounddevice and numpy to list audio devices.')
        print(sd.query_devices())
        return
    if not 0 <= args.volume <= 300:
        parser.error('--volume must be between 0 and 300.')
    if args.latency_ms is not None and not 1 <= args.latency_ms <= 1000:
        parser.error('--latency-ms must be between 1 and 1000.')
    volume_gain = args.volume / 100
    output_device = int(args.device) if args.device and args.device.isdecimal() else args.device
    output_latency = args.latency_ms / 1000 if args.latency_ms is not None else 'low'
    if not HAVE_AUDIO:
        parser.error('Install the sounddevice and numpy packages to play audio.')
    print(f'[*] Volume: {args.volume:g}% | Output: {output_device if output_device is not None else "system default"}')
    if args.volume_control_stdin:
        threading.Thread(target=volume_control_thread, daemon=True).start()
    print("=" * 65)
    print("   Xbox 360 Dedicated Audio Stream Receiver (Port 36000)")
    print("   Standardized Engine for Xbox360Audio.xex")
    print("=" * 65)

    player = threading.Thread(target=audio_player_thread, daemon=True)
    player.start()

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(("0.0.0.0", PORT))
    server_sock.listen(1)
    server_sock.settimeout(0.5)

    print(f"[*] Listening on 0.0.0.0:{PORT}...")
    print(f"[*] Waiting for Xbox 360 connection (Press Ctrl+C to stop)...")

    while not stop_event.is_set():
        try:
            try:
                client, addr = server_sock.accept()
            except socket.timeout:
                continue

            current_client_sock = client
            client.settimeout(0.5)
            client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            print(f"\n[+] Xbox 360 connected from {addr[0]}:{addr[1]}")

            byte_count = 0
            last_report = time.time()

            while not stop_event.is_set():
                try:
                    header = recv_exact(client, HEADER_SIZE)
                except socket.timeout:
                    continue

                (magic, codec, mode, w, h, quality, payload_bytes, frame_no, capture_us, encode_us) = struct.unpack(HEADER_FMT, header)

                if magic != MAGIC:
                    print(f"\n[!] Bad magic: 0x{magic:08X}, skipping")
                    continue

                payload = recv_exact(client, payload_bytes)
                byte_count += payload_bytes

                if codec == 3:  # Audio Packet
                    try:
                        audio_queue.put_nowait(payload)
                    except queue.Full:
                        try:
                            audio_queue.get_nowait()
                        except queue.Empty:
                            pass
                        try:
                            audio_queue.put_nowait(payload)
                        except queue.Full:
                            pass

                now = time.time()
                if now - last_report >= 0.5:
                    kbps = (byte_count * 8) / (1000.0 * (now - last_report))
                    db = compute_db(payload) if codec == 3 else 0.0
                    meter = "#" * max(0, min(20, int((db + 60) / 3)))
                    sys.stdout.write(f"\r[*] Audio: {quality}Hz {h}bit {w}ch | {kbps:6.1f} kbps | {db:5.1f} dB [{meter:<20s}]")
                    sys.stdout.flush()
                    byte_count = 0
                    last_report = now

        except (ConnectionResetError, ConnectionAbortedError, EOFError):
            if not stop_event.is_set():
                print("\n[-] Xbox disconnected. Waiting for reconnect...")
        except KeyboardInterrupt:
            break
        except Exception as e:
            if not stop_event.is_set():
                print(f"\n[!] Socket error: {e}. Retrying in 1s...")
                time.sleep(1)
        finally:
            if current_client_sock:
                try:
                    current_client_sock.close()
                except Exception:
                    pass
                current_client_sock = None

    print("\n[*] Receiver closed cleanly.")
    os._exit(0)

if __name__ == "__main__":
    main()
