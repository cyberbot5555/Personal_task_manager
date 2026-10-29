"""Settings view — preferences and startup help."""
from __future__ import annotations

import os
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox, ttk

from . import theme
from .. import config


class SettingsView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.columnconfigure(0, weight=1)

        ttk.Label(self, text="Settings", style="Title.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 14))

        card = tk.Frame(self, bg=theme.PANEL, highlightthickness=1,
                        highlightbackground=theme.BORDER)
        card.grid(row=1, column=0, sticky="ew")
        card.columnconfigure(1, weight=1)

        self.var_rem = tk.BooleanVar(
            value=bool(self.controller.state["prefs"].get("reminders_enabled", True)))
        self.var_startup = tk.BooleanVar(value=False)
        self.var_welcome = tk.StringVar(
            value=self.controller.state["prefs"].get("welcome_message", ""))

        def row(r, label):
            tk.Label(card, text=label, bg=theme.PANEL, fg=theme.TEXT,
                     font=("Segoe UI", 11), anchor="w").grid(
                row=r, column=0, sticky="w", padx=16, pady=10)

        row(0, "Enable desktop reminders")
        ttk.Checkbutton(card, variable=self.var_rem,
                        command=self._on_rem_toggle).grid(
            row=0, column=1, sticky="w", padx=16)

        row(1, "Welcome message")
        ttk.Entry(card, textvariable=self.var_welcome, width=40).grid(
            row=1, column=1, sticky="w", padx=16, pady=10)
        ttk.Button(card, text="Save message", style="Ghost.TButton",
                   command=self._save_welcome).grid(
            row=1, column=2, sticky="e", padx=(0, 16))

        row(2, "Start with Windows")
        ttk.Checkbutton(card, variable=self.var_startup,
                        command=self._on_startup_toggle).grid(
            row=2, column=1, sticky="w", padx=16)

        row(3, "Open startup folder")
        ttk.Button(card, text="📂 Open shell:startup",
                   style="Ghost.TButton", command=self._open_startup).grid(
            row=3, column=1, sticky="w", padx=16, pady=(0, 16))

        info = ttk.Label(
            self,
            style="Subtitle.TLabel",
            text=("Windows notifications: this app shows in-app reminder "
                  "popups using Tk. No hidden background process is created. "
                  "To start automatically at login, place a shortcut to "
                  "DailyTaskManager.exe in the shell:startup folder."),
            wraplength=700, justify="left")
        info.grid(row=2, column=0, sticky="ew", pady=(16, 0))

    def _on_rem_toggle(self) -> None:
        self.controller.state["prefs"]["reminders_enabled"] = bool(
            self.var_rem.get())
        self.controller.save_and_refresh()

    def _save_welcome(self) -> None:
        self.controller.state["prefs"]["welcome_message"] = (
            self.var_welcome.get().strip()
            or "Welcome back, operator. Stay sharp.")
        self.controller.save_and_refresh()

    def _on_startup_toggle(self) -> None:
        if self.var_startup.get():
            messagebox.showinfo(
                "Start with Windows",
                "This app does not create startup entries automatically.\n\n"
                "To enable autostart, place a shortcut to DailyTaskManager.exe "
                "inside the shell:startup folder. The button below opens it.",
                parent=self)
        # No silent autostart creation — user-driven only.

    def _open_startup(self) -> None:
        try:
            if sys.platform.startswith("win"):
                os.startfile(os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"))
            else:
                subprocess.Popen(["xdg-open", os.path.expanduser("~")])
        except Exception as exc:
            messagebox.showerror("Cannot open folder", str(exc), parent=self)

    def refresh(self):
        self.var_rem.set(bool(
            self.controller.state["prefs"].get("reminders_enabled", True)))
        self.var_welcome.set(
            self.controller.state["prefs"].get("welcome_message", ""))