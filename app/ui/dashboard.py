"""Dashboard view."""
from __future__ import annotations

import tkinter as tk
from datetime import date
from tkinter import ttk

from . import theme, widgets


class DashboardView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.columnconfigure(0, weight=1)
        self.rowconfigure(5, weight=1)

        # ---- Header ----
        header = ttk.Frame(self)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        header.columnconfigure(0, weight=1)
        ttk.Label(header, text="Dashboard", style="Title.TLabel").grid(
            row=0, column=0, sticky="w")
        self.date_lbl = ttk.Label(header, style="Subtitle.TLabel")
        self.date_lbl.grid(row=1, column=0, sticky="w", pady=(2, 0))

        # ---- Welcome ----
        self.welcome_lbl = ttk.Label(self, style="Subtitle.TLabel")
        self.welcome_lbl.grid(row=1, column=0, sticky="w", pady=(0, 16))

        # ---- Stat cards ----
        self.cards = ttk.Frame(self)
        self.cards.grid(row=2, column=0, sticky="ew")
        for i in range(4):
            self.cards.columnconfigure(i, weight=1, uniform="card")

        self.var_total = tk.StringVar(value="0")
        self.var_done = tk.StringVar(value="0")
        self.var_pending = tk.StringVar(value="0")
        self.var_pct = tk.StringVar(value="0%")

        widgets.stat_card(self.cards, "Total Tasks", self.var_total,
                          theme.ACCENT).grid(row=0, column=0, sticky="nsew",
                                             padx=(0, 8))
        widgets.stat_card(self.cards, "Completed", self.var_done,
                          theme.ACCENT_2).grid(row=0, column=1, sticky="nsew",
                                               padx=4)
        widgets.stat_card(self.cards, "Pending", self.var_pending,
                          theme.WARN).grid(row=0, column=2, sticky="nsew",
                                           padx=4)
        widgets.stat_card(self.cards, "Completion", self.var_pct,
                          theme.ACCENT).grid(row=0, column=3, sticky="nsew",
                                             padx=(8, 0))

        # ---- Progress bar ----
        prog_frame = ttk.Frame(self)
        prog_frame.grid(row=3, column=0, sticky="ew", pady=(18, 14))
        prog_frame.columnconfigure(0, weight=1)
        self.progress = ttk.Progressbar(
            prog_frame, style="Horizontal.TProgressbar",
            maximum=100, value=0)
        self.progress.grid(row=0, column=0, sticky="ew")

        # ---- Action buttons ----
        btns = ttk.Frame(self)
        btns.grid(row=4, column=0, sticky="ew", pady=(0, 14))
        ttk.Button(btns, text="+ Add Task", style="Accent.TButton",
                   command=self.controller.open_add_task).pack(side="left")
        ttk.Button(btns, text="Reset Today's Recurring Tasks",
                   style="Ghost.TButton",
                   command=self.controller.reset_today_recurring).pack(
            side="left", padx=8)
        ttk.Button(btns, text="View All Tasks", style="Ghost.TButton",
                   command=lambda: self.controller.show_view("tasks")
                   ).pack(side="left")

        # ---- Two list panels ----
        lists = ttk.Frame(self)
        lists.grid(row=5, column=0, sticky="nsew")
        lists.columnconfigure(0, weight=1)
        lists.columnconfigure(1, weight=1)
        lists.rowconfigure(0, weight=1)

        self.today_box = self._make_list_panel(lists, "Today's Tasks", 0)
        self.upcoming_box = self._make_list_panel(lists, "Upcoming & Overdue", 1)

    def _make_list_panel(self, parent, title, col):
        frame = ttk.Frame(parent, style="Panel.TFrame")
        frame.grid(row=0, column=col, sticky="nsew",
                   padx=(0, 8) if col == 0 else (8, 0))
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
        ttk.Label(frame, text=title, style="Panel.TLabel",
                  font=theme.FONT_HEADING).grid(
            row=0, column=0, sticky="w", padx=14, pady=(12, 8))
        lb = tk.Listbox(
            frame, bg=theme.PANEL, fg=theme.TEXT,
            selectbackground=theme.PANEL_ALT, selectforeground=theme.ACCENT,
            borderwidth=0, highlightthickness=0, activestyle="none",
            font=theme.FONT_BASE)
        lb.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        return lb

    def refresh(self):
        state = self.controller.state
        today = date.today().isoformat()
        self.date_lbl.config(text=f"Today: {today}")
        self.welcome_lbl.config(text=state["prefs"].get(
            "welcome_message", "Welcome back."))

        tasks = state["tasks"]
        todays = [t for t in tasks if t.get("created_date") == today]
        total = len(todays)
        done = sum(1 for t in todays if t.get("status") == "completed")
        pending = total - done
        pct = int((done / total) * 100) if total else 0

        self.var_total.set(str(total))
        self.var_done.set(str(done))
        self.var_pending.set(str(pending))
        self.var_pct.set(f"{pct}%")
        self.progress.config(value=pct)

        # Today's list
        self.today_box.delete(0, "end")
        for t in todays:
            mark = "[x]" if t.get("status") == "completed" else "[ ]"
            pr = {"High": "!!", "Medium": "!", "Low": "."}.get(
                t.get("priority"), ".")
            self.today_box.insert(
                "end",
                f"{mark} {pr}  {t.get('title')}   .   {t.get('category')}")
        if not todays:
            self.today_box.insert("end", "  No tasks for today yet.")

        # Upcoming & overdue
        self.upcoming_box.delete(0, "end")
        overdue = [t for t in tasks if self._is_overdue(t, today)]
        upcoming = [t for t in tasks
                    if t.get("due_date") and t.get("due_date") >= today
                    and t.get("status") != "completed"]
        for t in overdue:
            self.upcoming_box.insert(
                "end",
                f"!! OVERDUE  {t.get('title')}   due {t.get('due_date')}")
        for t in sorted(upcoming, key=lambda x: x.get("due_date", "")):
            self.upcoming_box.insert(
                "end",
                f"->  {t.get('title')}   due {t.get('due_date')}")
        if not overdue and not upcoming:
            self.upcoming_box.insert("end", "  Nothing scheduled.")

    @staticmethod
    def _is_overdue(t, today):
        if t.get("status") == "completed" or not t.get("due_date"):
            return False
        return t.get("due_date") < today