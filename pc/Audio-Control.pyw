"""Windowed entry point, including visible startup errors without a console."""
from pathlib import Path
import runpy
import traceback

try:
    runpy.run_path(str(Path(__file__).with_name('Audio-Control.py')), run_name='__main__')
except Exception:
    from tkinter import Tk, messagebox
    root = Tk()
    root.withdraw()
    messagebox.showerror('Xbox 360 Audio startup failed', traceback.format_exc())
    root.destroy()
