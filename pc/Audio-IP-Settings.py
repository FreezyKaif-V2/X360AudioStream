"""Set the Xbox audio receiver address via XBDM, without extra packages."""
import ipaddress
import re
import socket
import struct
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
from pathlib import Path

DESTINATION = r'HDD:\PERFORMER-AV.ini'
BACKUPS = Path(__file__).resolve().parent / 'config-backups'

def receiver_ip(value):
    address = ipaddress.IPv4Address(value.strip())
    if address.is_unspecified or address.is_loopback or address.is_multicast or int(address) == 0xffffffff:
        raise ValueError('Enter the PC network IPv4 address, not loopback, multicast or a broadcast address.')
    return str(address)

def read_exact(stream, n):
    data = bytearray()
    while len(data) < n:
        chunk = stream.read(n - len(data))
        if not chunk:
            raise EOFError('Console closed the connection')
        data.extend(chunk)
    return bytes(data)

def set_ip(content, ip):
    ip = receiver_ip(ip)
    text = content.removeprefix(b'\xef\xbb\xbf').decode('latin1')
    newline = '\r\n' if '\r\n' in text else '\n'
    lines = text.splitlines()
    result = []
    replaced = False
    for line in lines:
        if re.match(r'^\s*PC_IP\s*=', line, re.I):
            if not replaced:
                result.append('PC_IP=' + ip)
                replaced = True
        else:
            result.append(line)
    if not replaced:
        result.append('PC_IP=' + ip)
    return (newline.join(result) + newline).encode('latin1')

def apply_config(console, ip, port=730):
    console = console.strip()
    ipaddress.IPv4Address(console)
    ip = receiver_ip(ip)
    with socket.create_connection((console, port), timeout=5) as sock:
        sock.settimeout(8)
        f = sock.makefile('rwb', buffering=0)
        if not f.readline().startswith(b'201'):
            raise RuntimeError('Unexpected XBDM greeting')
        # Query the directory first so errors cannot be mistaken for absence.
        f.write(b'dirlist name="HDD:\\"\r\n')
        if not f.readline().startswith(b'202'):
            raise RuntimeError('Cannot list the console HDD')
        names = []
        while True:
            line = f.readline()
            if line == b'.\r\n':
                break
            if not line:
                raise EOFError('Incomplete directory listing')
            names.append(line.lower())
        exists = any(b'name="performer-av.ini"' in line for line in names)
        original = b''
        if exists:
            f.write(f'getfile name="{DESTINATION}"\r\n'.encode('ascii'))
            response = f.readline()
            if not response.startswith(b'203'):
                raise RuntimeError(f'Cannot read existing settings: {response!r}')
            size = struct.unpack('<I', read_exact(f, 4))[0]
            if size > 1024:
                raise RuntimeError('Existing settings exceed the XEX parser limit of 1023 bytes')
            original = read_exact(f, size)
            BACKUPS.mkdir(exist_ok=True)
            backup = BACKUPS / ('PERFORMER-AV-' + datetime.now().strftime('%Y%m%d-%H%M%S-%f') + '.ini')
            backup.write_bytes(original)
        data = set_ip(original, ip)
        if len(data) > 1023:
            raise RuntimeError('Settings exceed the XEX parser limit of 1023 bytes')
        f.write(f'sendfile name="{DESTINATION}" length=0x{len(data):x}\r\n'.encode('ascii'))
        response = f.readline()
        if not response.startswith(b'204'):
            raise RuntimeError(f'Console refused the upload: {response!r}')
        f.write(data)
        response = f.readline()
        if not response.startswith(b'200'):
            raise RuntimeError(f'Upload failed: {response!r}')
        f.write(f'getfile name="{DESTINATION}"\r\n'.encode('ascii'))
        if not f.readline().startswith(b'203'):
            raise RuntimeError('Uploaded settings could not be verified')
        size = struct.unpack('<I', read_exact(f, 4))[0]
        if size != len(data) or read_exact(f, size) != data:
            raise RuntimeError('Uploaded settings do not match')

def main():
    window = tk.Tk()
    window.title('Xbox 360 audio connection')
    window.resizable(False, False)
    frame = ttk.Frame(window, padding=18)
    frame.grid(sticky='nsew')
    console = tk.StringVar()
    receiver = tk.StringVar()
    ttk.Label(frame, text='Xbox IP address').grid(row=0, column=0, sticky='w', pady=6)
    ttk.Entry(frame, textvariable=console, width=20).grid(row=0, column=1, sticky='w')
    ttk.Label(frame, text='PC receiver address').grid(row=1, column=0, sticky='w', pady=6)
    ttk.Entry(frame, textvariable=receiver, width=20).grid(row=1, column=1, sticky='w')
    ttk.Label(frame, text='Enter full IPv4 addresses (for example 192.168.0.50 or 10.0.0.50). Requires XBDM on the Xbox. Reboot the Xbox after saving.', wraplength=350).grid(row=2, column=0, columnspan=2, pady=10)
    def save():
        try:
            ip = receiver_ip(receiver.get())
            apply_config(console.get().strip(), ip)
            messagebox.showinfo('Saved', f'PC address set to {ip} and read back successfully. Reboot the Xbox to apply it.')
        except (ValueError, OSError, RuntimeError, EOFError, UnicodeError) as exc:
            messagebox.showerror('Could not save', str(exc))
    ttk.Button(frame, text='Save to Xbox', command=save).grid(row=3, column=0, columnspan=2, pady=(4, 0))
    window.mainloop()

if __name__ == '__main__':
    main()
