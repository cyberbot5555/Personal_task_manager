"""Modal dialog for adding/editing a daily routine."""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional

from .. import config
from ..models import Routine
from . import theme


class RoutineFormDialog(tk.Toplevel):
    def __init__(self, master, existing: Optional[dict] = None):
        super().__init__(master)
        self.title("Edit Routine" if existing else "Add Routine")
        self.configure(bg=theme.BG)
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        self.result: Optional[dict] = None
        self._existing = existing

        self.var_title = tk.StringVar(value=existing.get("title", "") if existing else "")
        self.var_desc = tk.StringVar(value=existing.get("description", "") if existing else "")
        self.var_cat = tk.StringVar(value=existing.get("category", "General") if existing else "General")
        self.var_pri = tk.StringVar(value=existing.get("priority", "Medium") if existing else "Medium")
        self.var_rem = tk.StringVar(value=existing.get("reminder", "") if existing else "")

        container = tk.Frame(self, bg=theme.BG, padx=20, pady=20)
        container.pack(fill="both", expand=True)
        container.columnconfigure(1, weight=1)

        def row(r, label, widget):
            ttk.Label(container, text=label, style="TLabel").grid(
                row=r, column=0, sticky="w", pady=6, padx=(0, 8))
            widget.grid(row=r, column=1, sticky="ew", pady=6)

        row(0, "Title *", ttk.Entry(container, textvariable=self.var_title, width=40))
        row(1, "Description", ttk.Entry(container, textvariable=self.var_desc, width=40))
        cat = ttk.Combobox(container, textvariable=self.var_cat,
                           values=config.CATEGORIES, state="readonly", width=38)
        row(2, "Category", cat)
        pri = ttk.Combobox(container, textvariable=self.var_pri,
                           values=config.PRIORITIES, state="readonly", width=38)
        row(3, "Priority", pri)
        row(4, "Reminder (HH:MM)", ttk.Entry(container, textvariable=self.var_rem, width=40))

        btns = tk.Frame(self, bg=theme.BG, padx=20, pady=10)
        btns.pack(fill="x")
        ttk.Button(btns, text="Cancel", style="Ghost.TButton",
                   command=self._cancel).pack(side="right", padx=4)
        ttk.Button(btns, text="Save", style="Accent.TButton",
                   command=self._save).pack(side="right", padx=4)

        self.bind("<Escape>", lambda e: self._cancel())
        self.update_idletasks()
        try:
            px, py = master.winfo_rootx(), master.winfo_rooty()
            pw, ph = master.winfo_width(), master.winfo_height()
            w, h = self.winfo_width(), self.winfo_height()
            self.geometry(f"+{px + (pw - w) // 2}+{py + (ph - h) // 2}")
        except tk.TclError:
            pass

    def _save(self) -> None:
        if not self.var_title.get().strip():
            messagebox.showwarning("Missing title", "Title is required.", parent=self)
            return
        rem = self.var_rem.get().strip()
        if rem:
            try:
                hh, mm = rem.split(":")
                if not (0 <= int(hh) < 24 and 0 <= int(mm) < 60):
                    raise ValueError
            except (ValueError, IndexError):
                messagebox.showwarning("Invalid reminder",
                                       "Reminder must be HH:MM.", parent=self)
                return
        if self._existing:
            routine = dict(self._existing)
        else:
            routine = Routine(title="").to_dict()
        routine["title"] = self.var_title.get().strip()
        routine["description"] = self.var_desc.get().strip()
        routine["category"] = self.var_cat.get().strip() or "General"
        routine["priority"] = self.var_pri.get().strip() or "Medium"
        routine["reminder"] = rem
        self.result = routine
        self.destroy()

    def _cancel(self) -> None:
        self.result = None
        self.destroy()