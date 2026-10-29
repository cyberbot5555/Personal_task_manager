"""Tasks view: full CRUD, search, filters, overdue."""
from __future__ import annotations

import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk

from . import theme
from .. import config
from ..models import Task


class TasksView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)

        head = ttk.Frame(self)
        head.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        head.columnconfigure(0, weight=1)
        ttk.Label(head, text="Tasks", style="Title.TLabel").grid(
            row=0, column=0, sticky="w")
        ttk.Button(head, text="＋ Add Task", style="Accent.TButton",
                   command=self.controller.open_add_task).grid(
            row=0, column=1, sticky="e")

        bar = ttk.Frame(self)
        bar.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        bar.columnconfigure(0, weight=1)

        self.var_search = tk.StringVar()
        self.var_cat = tk.StringVar(value="All")
        self.var_pri = tk.StringVar(value="All")
        self.var_status = tk.StringVar(value="All")

        ttk.Entry(bar, textvariable=self.var_search).grid(
            row=0, column=0, sticky="ew", padx=(0, 8))
        ttk.Combobox(bar, textvariable=self.var_cat, state="readonly",
                     values=["All"] + config.CATEGORIES, width=22).grid(
            row=0, column=1, padx=4)
        ttk.Combobox(bar, textvariable=self.var_pri, state="readonly",
                     values=["All"] + config.PRIORITIES, width=12).grid(
            row=0, column=2, padx=4)
        ttk.Combobox(bar, textvariable=self.var_status, state="readonly",
                     values=["All", "pending", "completed"], width=12).grid(
            row=0, column=3, padx=(4, 0))

        for v in (self.var_search, self.var_cat, self.var_pri, self.var_status):
            v.trace_add("write", lambda *_: self.refresh())

        actions = ttk.Frame(self)
        actions.grid(row=2, column=0, sticky="ew", pady=(0, 8))
        ttk.Button(actions, text="✔ Toggle Status", style="Ghost.TButton",
                   command=self._toggle).pack(side="left")
        ttk.Button(actions, text="✎ Edit", style="Ghost.TButton",
                   command=self._edit).pack(side="left", padx=6)
        ttk.Button(actions, text="🗑 Delete", style="Danger.TButton",
                   command=self._delete).pack(side="left")

        cols = ("status", "title", "category", "priority", "due", "recurring")
        self.tree = ttk.Treeview(self, columns=cols, show="headings",
                                 selectmode="browse")
        for c, w, t in (
                ("status", 90, "Status"),
                ("title", 320, "Title"),
                ("category", 200, "Category"),
                ("priority", 90, "Priority"),
                ("due", 110, "Due"),
                ("recurring", 80, "Recurring")):
            self.tree.heading(c, text=t)
            self.tree.column(c, width=w, anchor="w")
        self.tree.grid(row=3, column=0, sticky="nsew")
        sb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        sb.grid(row=3, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.bind("<Double-1>", lambda e: self._edit())

    def _selected_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("No selection", "Select a task first.",
                                parent=self)
            return None
        return sel[0]

    def _toggle(self):
        tid = self._selected_id()
        if not tid:
            return
        for t in self.controller.state["tasks"]:
            if t.get("id") == tid:
                t["status"] = ("pending" if t.get("status") == "completed"
                               else "completed")
                t["completed_date"] = (date.today().isoformat()
                                       if t["status"] == "completed" else "")
                break
        self.controller.save_and_refresh()

    def _edit(self):
        tid = self._selected_id()
        if not tid:
            return
        task = next((t for t in self.controller.state["tasks"]
                     if t.get("id") == tid), None)
        if not task:
            return
        self.controller.open_edit_task(task)

    def _delete(self):
        tid = self._selected_id()
        if not tid:
            return
        if not messagebox.askyesno("Delete task",
                                   "Delete this task permanently?",
                                   parent=self):
            return
        self.controller.state["tasks"] = [
            t for t in self.controller.state["tasks"] if t.get("id") != tid
        ]
        self.controller.save_and_refresh()

    def refresh(self):
        tasks = self.controller.state["tasks"]
        search = self.var_search.get().strip().lower()
        cat = self.var_cat.get()
        pri = self.var_pri.get()
        status = self.var_status.get()
        filtered = []
        for t in tasks:
            if search and search not in t.get("title", "").lower():
                continue
            if cat != "All" and t.get("category") != cat:
                continue
            if pri != "All" and t.get("priority") != pri:
                continue
            if status != "All" and t.get("status") != status:
                continue
            filtered.append(t)

        for row in self.tree.get_children():
            self.tree.delete(row)
        for t in filtered:
            try:
                prio = t.get("priority", "Medium")
                self.tree.insert("", "end", iid=t.get("id"), values=(
                    t.get("status", ""),
                    t.get("title", ""),
                    t.get("category", ""),
                    prio,
                    t.get("due_date", "") or "-",
                    "⟳" if t.get("recurring") else "",
                ))
            except tk.TclError:
                continue