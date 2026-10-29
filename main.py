"""Entry point for Daily Task Manager.

Run with:  python main.py
"""
from __future__ import annotations

import ctypes
import sys
import traceback
import tkinter as tk
from tkinter import messagebox

from app import config
from app.ui.theme import apply_theme
from app.ui.main_window import MainWindow


def _enable_dpi_awareness() -> None:
    """Windows: sharper text on high-DPI screens."""
    if not sys.platform.startswith("win"):
        return
    try:
        # PROCESS_SYSTEM_DPI_AWARE = 1
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


def _excepthook(exc_type, exc_value, exc_tb):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_tb)
        return
    details = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    try:
        messagebox.showerror(
            f"{config.APP_NAME} — Unexpected error",
            f"An unexpected error occurred:\n\n{exc_value}",
        )
    except tk.TclError:
        pass
    print(details, file=sys.stderr)


def main() -> None:
    _enable_dpi_awareness()
    sys.excepthook = _excepthook
    root = tk.Tk()
    root.title(f"{config.APP_NAME} v{config.APP_VERSION}")
    root.minsize(1024, 640)
    root.configure(bg="#0b0f14")   # hard fallback in case theme fails
    apply_theme(root)
    MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()