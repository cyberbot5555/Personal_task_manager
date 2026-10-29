"""Main application shell: sidebar, views, shared state."""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from .. import config, routines as routines_mod, storage
from ..reminders import ReminderService
from . import theme
from .dashboard import DashboardView
from .tasks_view import TasksView
from .routines_view import RoutinesView
from .history_view import HistoryView
from .settings_view import SettingsView
from .task_form import TaskFormDialog


class MainWindow:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.state = {
            "tasks": storage.load_tasks(),
            "routines": storage.load_routines(),
            "history": storage.load_history(),
            "prefs": storage.load_prefs(),
        }

        # Restore window geometry
        geo = self.state["prefs"].get("window_geometry") or "1200x760"
        try:
            self.root.geometry(geo)
        except tk.TclError:
            self.root.geometry("1200x760")

        # Daily rollover
        try:
            if routines_mod.ensure_today(self.state):
                routines_mod.persist_all(self.state)
        except Exception as exc:
            messagebox.showerror("Rollover error", str(exc))

        self._build_shell()

        # Reminder service
        self.reminder = ReminderService(
            root,
            get_tasks=lambda: self.state["tasks"],
            notify=self._notify,
            enabled_getter=lambda: bool(
                self.state["prefs"].get("reminders_enabled", True)),
        )
        self.reminder.start()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.show_view("dashboard")

    # ---------------- Shell ------------------
    def _build_shell(self):
        shell = tk.Frame(self.root, bg=theme.BG)
        shell.pack(fill="both", expand=True)
        shell.columnconfigure(1, weight=1)
        shell.rowconfigure(0, weight=1)

        # ===== Sidebar =====
        sidebar = tk.Frame(shell, bg=theme.PANEL, width=220)
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.grid_propagate(False)
        sidebar.columnconfigure(0, weight=1)
        sidebar.rowconfigure(2, weight=1)

        # Brand
        brand = tk.Frame(sidebar, bg=theme.PANEL)
        brand.grid(row=0, column=0, sticky="ew", padx=16, pady=(20, 20))
        tk.Label(brand, text="◈", bg=theme.PANEL, fg=theme.ACCENT,
                 font=("Segoe UI Semibold", 24)).pack(side="left",
                                                       padx=(0, 10))
        btxt = tk.Frame(brand, bg=theme.PANEL)
        btxt.pack(side="left")
        tk.Label(btxt, text="Daily Task", bg=theme.PANEL, fg=theme.ACCENT,
                 font=("Segoe UI Semibold", 14), anchor="w").pack(
            anchor="w")
        tk.Label(btxt, text="Manager", bg=theme.PANEL, fg=theme.MUTED,
                 font=("Segoe UI", 10), anchor="w").pack(anchor="w")

        # Separator line
        tk.Frame(sidebar, bg=theme.BORDER, height=1).grid(
            row=1, column=0, sticky="ew", padx=12)

        # Nav buttons
        nav = tk.Frame(sidebar, bg=theme.PANEL)
        nav.grid(row=2, column=0, sticky="new", padx=10, pady=12)
        self._nav_buttons = {}
        for key, label, icon in (
                ("dashboard", "Dashboard", "▤"),
                ("tasks", "Tasks", "✔"),
                ("routines", "Routines", "⟳"),
                ("history", "History", "🕘"),
                ("settings", "Settings", "⚙")):
            btn = tk.Button(
                nav, text=f"  {icon}   {label}", anchor="w",
                bg=theme.PANEL, fg=theme.TEXT_SOFT,
                activebackground=theme.PANEL_ALT,
                activeforeground=theme.ACCENT,
                bd=0, relief="flat",
                font=("Segoe UI", 12),
                padx=14, pady=10, cursor="hand2", highlightthickness=0,
                command=lambda k=key: self.show_view(k))
            btn.pack(fill="x", pady=2)
            self._nav_buttons[key] = btn

        # Status footer
        status = tk.Frame(sidebar, bg=theme.PANEL)
        status.grid(row=3, column=0, sticky="ew", padx=16, pady=14)
        tk.Label(status, text="●", bg=theme.PANEL, fg=theme.ACCENT,
                 font=("Segoe UI", 12)).pack(side="left")
        tk.Label(status, text="  Offline · Local data", bg=theme.PANEL,
                 fg=theme.MUTED, font=("Segoe UI", 10)).pack(side="left")

        # ===== Content =====
        self.content = tk.Frame(shell, bg=theme.BG, padx=28, pady=24)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.columnconfigure(0, weight=1)
        self.content.rowconfigure(0, weight=1)

        self.views = {
            "dashboard": DashboardView(self.content, self),
            "tasks": TasksView(self.content, self),
            "routines": RoutinesView(self.content, self),
            "history": HistoryView(self.content, self),
            "settings": SettingsView(self.content, self),
        }
        for v in self.views.values():
            v.grid(row=0, column=0, sticky="nsew")
            v.grid_remove()

    def show_view(self, key: str) -> None:
        """Switch to a view and update nav button highlight."""
        for k, v in self.views.items():
            if k == key:
                v.grid(row=0, column=0, sticky="nsew")
                v.tkraise()
            else:
                v.grid_remove()

        for k, btn in self._nav_buttons.items():
            is_active = (k == key)
            btn.configure(
                bg=theme.PANEL_ALT if is_active else theme.PANEL,
                fg=theme.ACCENT if is_active else theme.TEXT_SOFT,
                font=("Segoe UI Semibold", 12) if is_active
                     else ("Segoe UI", 12),
            )

        try:
            if key in self.views:
                self.views[key].refresh()
        except Exception:
            pass

    def _refresh_all(self) -> None:
        for v in self.views.values():
            try:
                v.refresh()
            except Exception:
                pass

    # ---------------- Data actions ------------------
    def save_and_refresh(self) -> None:
        try:
            routines_mod.persist_all(self.state)
        except Exception as exc:
            messagebox.showerror("Save error", str(exc))
            return
        self._refresh_all()

    def open_add_task(self) -> None:
        dlg = TaskFormDialog(self.root)
        self.root.wait_window(dlg)
        if dlg.result:
            self.state["tasks"].append(dlg.result)
            self.save_and_refresh()

    def open_edit_task(self, task: dict) -> None:
        dlg = TaskFormDialog(self.root, existing=task)
        self.root.wait_window(dlg)
        if dlg.result:
            tasks = self.state["tasks"]
            for i, t in enumerate(tasks):
                if t.get("id") == task.get("id"):
                    tasks[i] = dlg.result
                    break
            self.save_and_refresh()

    def reset_today_recurring(self) -> None:
        if not messagebox.askyesno(
                "Reset today's recurring tasks",
                "Delete today's recurring tasks and regenerate them?\n\n"
                "History from previous days and routine definitions "
                "will be preserved.",
                parent=self.root):
            return
        try:
            routines_mod.reset_today_recurring(self.state)
            self.save_and_refresh()
        except Exception as exc:
            messagebox.showerror("Reset error", str(exc))

    # ---------------- Reminders ------------------
    def _notify(self, title: str, body: str) -> None:
        try:
            messagebox.showinfo(title, body, parent=self.root)
            try:
                import winsound
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
            except Exception:
                pass
        except Exception:
            pass

    # ---------------- Shutdown ------------------
    def _on_close(self) -> None:
        try:
            self.state["prefs"]["window_geometry"] = self.root.geometry()
            routines_mod.persist_all(self.state)
        except Exception:
            pass
        self.reminder.stop()
        self.root.destroy()