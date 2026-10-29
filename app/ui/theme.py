"""Dark cybersecurity theme — high contrast, sharp typography."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

# ===== Palette =====
BG = "#0b0f14"
PANEL = "#151b23"
PANEL_ALT = "#1e2733"
BORDER = "#303a47"
BORDER_SOFT = "#242c37"

ACCENT = "#00ff9c"
ACCENT_DIM = "#00c97c"
ACCENT_2 = "#00d9ff"
TEXT = "#eef3f8"
TEXT_SOFT = "#c9d1d9"
MUTED = "#8b98a5"
DANGER = "#ff6b6b"
WARN = "#ffb86c"
OK = "#00ff9c"

# ===== Typography =====
FONT_BASE = ("Segoe UI", 11)
FONT_SMALL = ("Segoe UI", 10)
FONT_MUTED = ("Segoe UI", 10)
FONT_LABEL = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI Semibold", 11)
FONT_TITLE = ("Segoe UI Semibold", 22)
FONT_SUBTITLE = ("Segoe UI", 11)
FONT_CARD_VALUE = ("Segoe UI Semibold", 30)
FONT_CARD_LABEL = ("Segoe UI", 10)
FONT_NAV = ("Segoe UI Semibold", 12)
FONT_BUTTON = ("Segoe UI Semibold", 11)
FONT_HEADING = ("Segoe UI Semibold", 13)


def apply_theme(root: tk.Tk) -> None:
    root.configure(bg=BG)

    # ============ GLOBAL DEFAULTS for CLASSIC tk widgets ============
    # ttk.Style does NOT affect tk.Label/tk.Button/tk.Listbox/tk.Entry/etc.
    # These root-level defaults fix "black font" and small fonts everywhere.
    defaults = {
        "*Font": FONT_BASE,
        "*Background": BG,
        "*Foreground": TEXT,
        "*Label.Font": FONT_BASE,
        "*Label.Background": BG,
        "*Label.Foreground": TEXT,
        "*Button.Font": FONT_BUTTON,
        "*Button.Background": PANEL,
        "*Button.Foreground": TEXT,
        "*Listbox.Font": FONT_BASE,
        "*Listbox.Background": PANEL,
        "*Listbox.Foreground": TEXT,
        "*Listbox.SelectBackground": PANEL_ALT,
        "*Listbox.SelectForeground": ACCENT,
        "*Entry.Font": FONT_BASE,
        "*Entry.Background": PANEL_ALT,
        "*Entry.Foreground": TEXT,
        "*Entry.InsertBackground": ACCENT,
        "*Text.Font": FONT_BASE,
        "*Text.Background": PANEL_ALT,
        "*Text.Foreground": TEXT,
        "*Text.InsertBackground": ACCENT,
        "*Toplevel.Background": BG,
        "*Menu.Background": PANEL,
        "*Menu.Foreground": TEXT,
        "*Menu.Font": FONT_BASE,
        "*Menu.ActiveBackground": PANEL_ALT,
        "*Menu.ActiveForeground": ACCENT,
        "*Checkbutton.Font": FONT_BASE,
        "*Checkbutton.Background": PANEL,
        "*Checkbutton.Foreground": TEXT,
    }
    for key, val in defaults.items():
        try:
            root.option_add(key, val)
        except tk.TclError:
            pass

    # ============ ttk theme ============
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    # Base
    style.configure(".", background=BG, foreground=TEXT,
                    fieldbackground=PANEL, font=FONT_BASE, borderwidth=0)
    style.configure("TFrame", background=BG)
    style.configure("Panel.TFrame", background=PANEL)

    # Labels
    style.configure("TLabel", background=BG, foreground=TEXT, font=FONT_BASE)
    style.configure("Panel.TLabel", background=PANEL, foreground=TEXT,
                    font=FONT_BASE)
    style.configure("Muted.TLabel", background=BG, foreground=MUTED,
                    font=FONT_MUTED)
    style.configure("Title.TLabel", background=BG, foreground=ACCENT,
                    font=FONT_TITLE)
    style.configure("Subtitle.TLabel", background=BG, foreground=TEXT_SOFT,
                    font=FONT_SUBTITLE)
    style.configure("Heading.TLabel", background=BG, foreground=ACCENT,
                    font=FONT_HEADING)

    # Nav buttons
    style.configure("Nav.TButton", background=PANEL, foreground=TEXT_SOFT,
                    borderwidth=0, padding=(16, 12), anchor="w",
                    font=FONT_NAV)
    style.map("Nav.TButton",
              background=[("active", PANEL_ALT), ("pressed", PANEL_ALT)],
              foreground=[("active", ACCENT), ("pressed", ACCENT)])

    # Accent button
    style.configure("Accent.TButton", background=ACCENT, foreground="#04140b",
                    borderwidth=0, padding=(16, 10), font=FONT_BUTTON,
                    focuscolor=ACCENT)
    style.map("Accent.TButton",
              background=[("active", ACCENT_2), ("pressed", ACCENT_DIM)],
              foreground=[("active", "#04140b"), ("pressed", "#04140b")])

    # Ghost button
    style.configure("Ghost.TButton", background=PANEL, foreground=TEXT,
                    borderwidth=1, bordercolor=BORDER, padding=(14, 9),
                    font=FONT_BUTTON, focuscolor=ACCENT)
    style.map("Ghost.TButton",
              background=[("active", PANEL_ALT), ("pressed", PANEL_ALT)],
              bordercolor=[("active", ACCENT)],
              foreground=[("active", ACCENT)])

    # Danger button
    style.configure("Danger.TButton", background=DANGER, foreground="#180404",
                    borderwidth=0, padding=(14, 9), font=FONT_BUTTON)
    style.map("Danger.TButton",
              background=[("active", "#ff8585"), ("pressed", "#e05555")],
              foreground=[("active", "#180404")])

    # Entry
    style.configure("TEntry", fieldbackground=PANEL_ALT, foreground=TEXT,
                    insertcolor=ACCENT, bordercolor=BORDER,
                    lightcolor=BORDER, darkcolor=BORDER, padding=8,
                    font=FONT_BASE)
    style.map("TEntry",
              bordercolor=[("focus", ACCENT)],
              lightcolor=[("focus", ACCENT)],
              darkcolor=[("focus", ACCENT)])

    # Combobox
    style.configure("TCombobox", fieldbackground=PANEL_ALT, background=PANEL_ALT,
                    foreground=TEXT, arrowcolor=ACCENT, bordercolor=BORDER,
                    lightcolor=BORDER, darkcolor=BORDER, padding=6,
                    font=FONT_BASE)
    style.map("TCombobox",
              fieldbackground=[("readonly", PANEL_ALT)],
              foreground=[("readonly", TEXT)],
              bordercolor=[("focus", ACCENT)],
              arrowcolor=[("active", ACCENT_2)])

    # Combobox dropdown listbox (special — needs option_add)
    for key, val in (
            ("*TCombobox*Listbox.background", PANEL_ALT),
            ("*TCombobox*Listbox.foreground", TEXT),
            ("*TCombobox*Listbox.selectBackground", ACCENT),
            ("*TCombobox*Listbox.selectForeground", "#04140b"),
            ("*TCombobox*Listbox.font", FONT_BASE)):
        try:
            root.option_add(key, val)
        except tk.TclError:
            pass

    # Treeview
    style.configure("Treeview", background=PANEL, fieldbackground=PANEL,
                    foreground=TEXT, rowheight=34, borderwidth=0,
                    font=FONT_BASE)
    style.configure("Treeview.Heading", background=PANEL_ALT, foreground=ACCENT,
                    borderwidth=0, font=FONT_BOLD, padding=(10, 10))
    style.map("Treeview",
              background=[("selected", PANEL_ALT)],
              foreground=[("selected", ACCENT)])
    style.map("Treeview.Heading",
              background=[("active", BORDER)])

    # Progressbar
    style.configure("Horizontal.TProgressbar", background=ACCENT,
                    troughcolor=PANEL_ALT, bordercolor=BORDER,
                    lightcolor=ACCENT, darkcolor=ACCENT, thickness=12)
    style.configure("Cyan.Horizontal.TProgressbar", background=ACCENT_2,
                    troughcolor=PANEL_ALT, bordercolor=BORDER,
                    lightcolor=ACCENT_2, darkcolor=ACCENT_2, thickness=12)

    # Scrollbar
    style.configure("Vertical.TScrollbar", background=PANEL_ALT,
                    troughcolor=BG, bordercolor=BG, arrowcolor=MUTED,
                    width=12)
    style.map("Vertical.TScrollbar",
              background=[("active", BORDER)])

    # Checkbutton
    style.configure("TCheckbutton", background=PANEL, foreground=TEXT,
                    font=FONT_BASE, indicatorcolor=PANEL_ALT)
    style.map("TCheckbutton",
              background=[("active", PANEL)],
              foreground=[("active", ACCENT)],
              indicatorcolor=[("selected", ACCENT)])

    # Separator
    style.configure("TSeparator", background=BORDER)