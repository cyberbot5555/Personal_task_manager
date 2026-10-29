"""Modal dialog for adding/editing a single task."""
from __future__ import annotations

import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk
from typing import Optional

from .. import config
from ..models import Task
from . import theme


class TaskFormDialog(tk.Toplevel):
    """Returns a Task dict (or None if cancelled) via self.result."""

    def __init__(self, master, existing: Optional[dict] = None):
        super().__init__(master)
        self.title("Edit Task" if existing else "Add Task")
        self.configure(bg=theme.BG)
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        self.result: Optional[dict] = None
        self._saving = False
        self._existing = existing

        self.var_title = tk.StringVar(
            value=existing.get("title", "") if existing else "")
        self.var_desc = tk.StringVar(
            value=existing.get("description", "") if existing else "")
        self.var_cat = tk.StringVar(
            value=existing.get("category", "General") if existing else "General")
        self.var_pri = tk.StringVar(
            value=existing.get("priority", "Medium") if existing else "Medium")
        self.var_due = tk.StringVar(
            value=existing.get("due_date", "") if existing else "")
        self.var_dtime = tk.StringVar(
            value=existing.get("due_time", "") if existing else "")
        self.var_rem = tk.StringVar(
            value=existing.get("reminder", "") if existing else "")

        container = tk.Frame(self, bg=theme.BG, padx=20, pady=20)
        container.pack(fill="both", expand=True)
        container.columnconfigure(1, weight=1)

        def add_row(r, label, widget):
            ttk.Label(container, text=label, style="TLabel").grid(
                row=r, column=0, sticky="w", pady=6, padx=(0, 8))
            widget.grid(row=r, column=1, sticky="ew", pady=6)

        add_row(0, "Title *",
                ttk.Entry(container, textvariable=self.var_title, width=40))
        add_row(1, "Description",
                ttk.Entry(container, textvariable=self.var_desc, width=40))
        add_row(2, "Category",
                ttk.Combobox(container, textvariable=self.var_cat,
                             values=config.CATEGORIES, state="readonly",
                             width=38))
        add_row(3, "Priority",
                ttk.Combobox(container, textvariable=self.var_pri,
                             values=config.PRIORITIES, state="readonly",
                             width=38))
        add_row(4, "Due date (YYYY-MM-DD)",
                ttk.Entry(container, textvariable=self.var_due, width=40))
        add_row(5, "Due time (HH:MM optional)",
                ttk.Entry(container, textvariable=self.var_dtime, width=40))
        add_row(6, "Reminder (HH:MM optional)",
                ttk.Entry(container, textvariable=self.var_rem, width=40))

        btns = tk.Frame(self, bg=theme.BG, padx=20, pady=10)
        btns.pack(fill="x")
        ttk.Button(btns, text="Cancel", style="Ghost.TButton",
                   command=self._cancel).pack(side="right", padx=4)
        ttk.Button(btns, text="Save", style="Accent.TButton",
                   command=self._save).pack(side="right", padx=4)

        self.bind("<Escape>", lambda e: self._cancel())
        self.bind("<Return>", lambda e: self._save())
        self.update_idletasks()
        try:
            px, py = master.winfo_rootx(), master.winfo_rooty()
            pw, ph = master.winfo_width(), master.winfo_height()
            w, h = self.winfo_width(), self.winfo_height()
            self.geometry(f"+{px + (pw - w) // 2}+{py + (ph - h) // 2}")
        except tk.TclError:
            pass

    def _validate(self) -> bool:
        if not self.var_title.get().strip():
            messagebox.showwarning("Missing title",
                                   "Title is required.", parent=self)
            return False
        due = self.var_due.get().strip()
        if due:
            try:
                date.fromisoformat(due)
            except ValueError:
                messagebox.showwarning(
                    "Invalid due date",
                    "Due date must be YYYY-MM-DD.", parent=self)
                return False
        for label, val in (("Due time", self.var_dtime.get().strip()),
                           ("Reminder", self.var_rem.get().strip())):
            if val:
                try:
                    parts = val.split(":")
                    if len(parts) != 2:
                        raise ValueError
                    hh, mm = int(parts[0]), int(parts[1])
                    if not (0 <= hh < 24 and 0 <= mm < 60):
                        raise ValueError
                except ValueError:
                    messagebox.showwarning(
                        "Invalid time",
                        f"{label} must be HH:MM.", parent=self)
                    return False
        return True

    def _save(self) -> None:
        if self._saving:
            return
        self._saving = True
        try:
            if not self._validate():
                return
            if self._existing:
                task = dict(self._existing)
            else:
                task = Task(title="").to_dict()
            task["title"] = self.var_title.get().strip()
            task["description"] = self.var_desc.get().strip()
            task["category"] = self.var_cat.get().strip() or "General"
            task["priority"] = self.var_pri.get().strip() or "Medium"
            task["due_date"] = self.var_due.get().strip()
            task["due_time"] = self.var_dtime.get().strip()
            task["reminder"] = self.var_rem.get().strip()
            self.result = task
            self.destroy()
        finally:
            self._saving = False

    def _cancel(self) -> None:
        self.result = None
        self.destroy()