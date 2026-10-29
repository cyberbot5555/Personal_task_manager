"""Reusable UI widgets."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from . import theme


def stat_card(parent, label: str, value_var: tk.StringVar,
              accent: str = theme.ACCENT) -> tk.Frame:
    """Dashboard stat card with left accent strip and larger values."""
    outer = tk.Frame(parent, bg=theme.PANEL, highlightthickness=1,
                     highlightbackground=theme.BORDER)
    # Left accent strip
    strip = tk.Frame(outer, bg=accent, width=4)
    strip.pack(side="left", fill="y")
    inner = tk.Frame(outer, bg=theme.PANEL)
    inner.pack(side="left", fill="both", expand=True, padx=16, pady=14)
    tk.Label(inner, text=label.upper(), bg=theme.PANEL, fg=theme.MUTED,
             font=theme.FONT_CARD_LABEL, anchor="w").pack(fill="x")
    tk.Label(inner, textvariable=value_var, bg=theme.PANEL, fg=accent,
             font=theme.FONT_CARD_VALUE, anchor="w").pack(fill="x", pady=(2, 0))
    return outer