"""Previous days' completion records."""
from __future__ import annotations

from tkinter import ttk

from . import theme


class HistoryView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        ttk.Label(self, text="History", style="Title.TLabel").grid(
            row=0, column=0, sticky="w")
        ttk.Label(self, style="Subtitle.TLabel",
                  text="Completion records archived each day.").grid(
            row=1, column=0, sticky="w", pady=(0, 10))

        cols = ("date", "total", "completed", "pct")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for c, w, t in (
                ("date", 140, "Date"),
                ("total", 100, "Total"),
                ("completed", 100, "Completed"),
                ("pct", 100, "%")):
            self.tree.heading(c, text=t)
            self.tree.column(c, width=w, anchor="center")
        self.tree.grid(row=2, column=0, sticky="nsew")
        sb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        sb.grid(row=2, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=sb.set)

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        history = self.controller.state["history"]
        for day in sorted(history.keys(), reverse=True):
            bucket = history[day]
            total = bucket.get("total", len(bucket.get("tasks", [])))
            done = bucket.get("completed",
                              sum(1 for t in bucket.get("tasks", [])
                                  if t.get("status") == "completed"))
            pct = f"{int(done / total * 100)}%" if total else "0%"
            self.tree.insert("", "end", values=(day, total, done, pct))