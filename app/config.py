"""Application-wide constants, paths, and defaults."""
from __future__ import annotations

import os
import sys
from pathlib import Path

APP_NAME = "Daily Task Manager"
APP_ID = "DailyTaskManager"
APP_VERSION = "1.0.0"


def get_data_dir() -> Path:
    """Return the persistent data directory.

    Uses %LOCALAPPDATA%\\DailyTaskManager on Windows, with a cross-platform
    fallback for development. Never uses PyInstaller's _MEIPASS temp dir.
    """
    if sys.platform.startswith("win"):
        base = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
        data_dir = Path(base) / APP_ID
    else:
        data_dir = Path.home() / ".daily_task_manager"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


DATA_DIR = get_data_dir()
BACKUP_DIR = DATA_DIR / "backups"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

TASKS_FILE = DATA_DIR / "tasks.json"
ROUTINES_FILE = DATA_DIR / "routines.json"
HISTORY_FILE = DATA_DIR / "history.json"
PREFS_FILE = DATA_DIR / "prefs.json"

MAX_BACKUPS = 10

CATEGORIES = [
    "CSE / Academic",
    "Cybersecurity / SOC Lab",
    "Digital Forensics CTF",
    "Reverse Engineering",
    "Networking / Linux",
    "Personal Project",
    "Review & Planning",
    "General",
]

PRIORITIES = ["High", "Medium", "Low"]
STATUSES = ["pending", "completed"]

DEFAULT_ROUTINES = [
    {"title": "CSE & academic study", "category": "CSE / Academic",
     "priority": "High", "description": "Study core CSE subjects.",
     "reminder": "09:00"},
    {"title": "Cybersecurity / SOC lab practice", "category": "Cybersecurity / SOC Lab",
     "priority": "High", "description": "Practice SOC analysis & blue-team labs.",
     "reminder": "11:00"},
    {"title": "Digital forensics CTF practice", "category": "Digital Forensics CTF",
     "priority": "Medium", "description": "Solve one forensic CTF challenge.",
     "reminder": "14:00"},
    {"title": "Reverse engineering practice", "category": "Reverse Engineering",
     "priority": "Medium", "description": "Analyze a binary / crackme.",
     "reminder": "16:00"},
    {"title": "Networking & Linux practice", "category": "Networking / Linux",
     "priority": "Medium", "description": "Packet analysis + Linux CLI drills.",
     "reminder": "18:00"},
    {"title": "Personal project work", "category": "Personal Project",
     "priority": "Low", "description": "Advance a personal project.",
     "reminder": "20:00"},
    {"title": "Daily review & planning", "category": "Review & Planning",
     "priority": "Low", "description": "Review day, plan tomorrow.",
     "reminder": "21:30"},
]

DEFAULT_PREFS = {
    "last_seen_date": "",
    "reminders_enabled": True,
    "welcome_message": "Welcome back, operator. Stay sharp.",
    "window_geometry": "1200x760",
}