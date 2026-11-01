"""Simple launcher for Xbox audio playback and connection settings."""
import queue
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

HERE = Path(__file__).resolve().parent
PYTHON = str(Path(sys.executable).with_name('python.exe')) if sys.platform == 'win32' else sys.executable
HIDDEN_PROCESS = {'creationflags': subprocess.CREATE_NO_WINDOW} if sys.platform == 'win32' else {}
try:
    import sounddevice as sd
except ImportError:
    sd = None

class AudioControl:
    def __init__(self, root):
        self.root = root
        self.process = None
        self.messages = queue.Queue()
        self.volume = tk.DoubleVar(value=200)
        self.volume_label = tk.StringVar(value='200%')
        self.volume_status = tk.StringVar(value='Volume applies when audio starts')
        root.title('Xbox 360 Audio')
        root.protocol('WM_DELETE_WINDOW', self.close)
        frame = ttk.Frame(root, padding=14)
        frame.pack(fill='both', expand=True)
        ttk.Label(frame, text='Xbox 360 Audio', font=('Segoe UI', 16, 'bold')).pack(anchor='w')
        controls = ttk.Frame(frame)
        controls.pack(fill='x', pady=(12, 6))
        ttk.Label(controls, text='Volume').pack(side='left')
        ttk.Scale(controls, from_=0, to=300, variable=self.volume, orient='horizontal', command=self.set_volume).pack(side='left', fill='x', expand=True, padx=8)
        ttk.Label(controls, textvariable=self.volume_label, width=6).pack(side='left')
        ttk.Label(frame, textvariable=self.volume_status).pack(anchor='w')
        ttk.Label(frame, text='Adjust volume while playing. Above 100% can distort loud sounds.', wraplength=480).pack(anchor='w')
        output = ttk.Frame(frame)
        output.pack(fill='x', pady=(10, 0))
        ttk.Label(output, text='Output').pack(side='left', padx=(0, 8))
        self.devices = [('System default', None)]
        if sd:
            try:
                hosts = sd.query_hostapis()
                for index, device in enumerate(sd.query_devices()):
                    if device['max_output_channels'] >= 2:
                        name = f"{index}: {device['name']} ({hosts[device['hostapi']]['name']})"
                        self.devices.append((name, index))
            except Exception:
                pass
        self.device = ttk.Combobox(output, state='readonly', values=[name for name, _ in self.devices], width=55)
        self.device.current(0)
        self.device.pack(side='left', fill='x', expand=True)
        buttons = ttk.Frame(frame)
        buttons.pack(fill='x', pady=10)
        self.start_button = ttk.Button(buttons, text='Start audio', command=self.start)
        self.start_button.pack(side='left', padx=(0, 8))
        self.stop_button = ttk.Button(buttons, text='Stop audio', command=self.stop, state='disabled')
        self.stop_button.pack(side='left', padx=(0, 8))
        ttk.Button(buttons, text='Xbox connection settings', command=self.settings).pack(side='left')
        self.log = tk.Text(frame, width=75, height=14, wrap='word', state='disabled')
        self.log.pack(fill='both', expand=True)
        root.after(100, self.update)

    def start(self):
        if self.process and self.process.poll() is None:
            return
        try:
            command = [PYTHON, '-u', str(HERE / 'PC-Audio-Receiver.py'), '--volume', str(self.volume.get()), '--volume-control-stdin']
            selected_device = self.devices[self.device.current()][1]
            if selected_device is not None:
                command += ['--device', str(selected_device)]
            self.process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding='utf-8', errors='replace', bufsize=1, **HIDDEN_PROCESS)
        except OSError as exc:
            messagebox.showerror('Could not start audio', str(exc))
            return
        process = self.process
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        def collect():
            for line in process.stdout:
                self.messages.put(line)
            self.messages.put('\nReceiver stopped.\n')
        threading.Thread(target=collect, daemon=True).start()

    def set_volume(self, value):
        percent = round(float(value))
        self.volume_label.set(f'{percent}%')
        if self.process and self.process.poll() is None:
            try:
                self.process.stdin.write(f'{percent}\n')
                self.process.stdin.flush()
                self.volume_status.set(f'Applying {percent}%…')
            except (OSError, ValueError):
                self.volume_status.set('Volume update failed — restart audio')

    def stop(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()

    def settings(self):
        try:
            subprocess.Popen([PYTHON, str(HERE / 'Audio-IP-Settings.py')], **HIDDEN_PROCESS)
        except OSError as exc:
            messagebox.showerror('Could not open settings', str(exc))

    def update(self):
        while True:
            try:
                message = self.messages.get_nowait()
            except queue.Empty:
                break
            if '[volume] ' in message:
                self.volume_status.set(message.split('[volume] ', 1)[1].strip())
                continue
            self.log.config(state='normal')
            self.log.insert('end', message)
            self.log.see('end')
            self.log.config(state='disabled')
        if self.process and self.process.poll() is not None:
            self.process = None
            self.start_button.config(state='normal')
            self.stop_button.config(state='disabled')
        self.root.after(100, self.update)

    def close(self):
        self.stop()
        self.root.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    AudioControl(root)
    root.mainloop()
