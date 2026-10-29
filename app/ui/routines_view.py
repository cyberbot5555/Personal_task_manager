"""Routines editor."""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from . import theme
from .routine_form import RoutineFormDialog


class RoutinesView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        head = ttk.Frame(self)
        head.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        head.columnconfigure(0, weight=1)
        ttk.Label(head, text="Daily Routines", style="Title.TLabel").grid(
            row=0, column=0, sticky="w")
        ttk.Button(head, text="＋ Add Routine", style="Accent.TButton",
                   command=self._add).grid(row=0, column=1)

        ttk.Label(self, style="Subtitle.TLabel",
                  text=("Routines generate a fresh recurring task each day. "
                        "Editing here won't affect previous days.")).grid(
            row=1, column=0, sticky="w", pady=(0, 10))

        cols = ("title", "category", "priority", "reminder", "active")
        self.tree = ttk.Treeview(self, columns=cols, show="headings",
                                 selectmode="browse")
        for c, w, t in (
                ("title", 300, "Title"),
                ("category", 200, "Category"),
                ("priority", 90, "Priority"),
                ("reminder", 90, "Reminder"),
                ("active", 80, "Active")):
            self.tree.heading(c, text=t)
            self.tree.column(c, width=w, anchor="w")
        self.tree.grid(row=2, column=0, sticky="nsew")
        sb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        sb.grid(row=2, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.bind("<Double-1>", lambda e: self._edit())

        actions = ttk.Frame(self)
        actions.grid(row=3, column=0, sticky="ew", pady=(8, 0))
        ttk.Button(actions, text="✎ Edit", style="Ghost.TButton",
                   command=self._edit).pack(side="left")
        ttk.Button(actions, text="🗑 Delete", style="Danger.TButton",
                   command=self._delete).pack(side="left", padx=6)
        ttk.Button(actions, text="Toggle Active", style="Ghost.TButton",
                   command=self._toggle_active).pack(side="left")

    def _selected_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("No selection", "Select a routine first.",
                                parent=self)
            return None
        return sel[0]

    def _add(self):
        dlg = RoutineFormDialog(self.winfo_toplevel())
        self.wait_window(dlg)
        if dlg.result:
            self.controller.state["routines"].append(dlg.result)
            self.controller.save_and_refresh()

    def _edit(self):
        rid = self._selected_id()
        if not rid:
            return
        routine = next((r for r in self.controller.state["routines"]
                        if r.get("id") == rid), None)
        if not routine:
            return
        dlg = RoutineFormDialog(self.winfo_toplevel(), routine)
        self.wait_window(dlg)
        if dlg.result:
            routines = self.controller.state["routines"]
            for i, r in enumerate(routines):
                if r.get("id") == rid:
                    routines[i] = dlg.result
                    break
            self.controller.save_and_refresh()

    def _delete(self):
        rid = self._selected_id()
        if not rid:
            return
        if not messagebox.askyesno(
                "Delete routine",
                "Delete this routine? Existing generated tasks are kept.",
                parent=self):
            return
        self.controller.state["routines"] = [
            r for r in self.controller.state["routines"] if r.get("id") != rid
        ]
        self.controller.save_and_refresh()

    def _toggle_active(self):
        rid = self._selected_id()
        if not rid:
            return
        for r in self.controller.state["routines"]:
            if r.get("id") == rid:
                r["active"] = not r.get("active", True)
                break
        self.controller.save_and_refresh()

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for r in self.controller.state["routines"]:
            try:
                self.tree.insert("", "end", iid=r.get("id"), values=(
                    r.get("title", ""),
                    r.get("category", ""),
                    r.get("priority", ""),
                    r.get("reminder", "") or "-",
                    "Yes" if r.get("active", True) else "No",
                ))
            except tk.TclError:
                continue