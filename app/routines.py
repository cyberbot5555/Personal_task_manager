"""Daily rollover: generate recurring tasks once per day, archive history."""
from __future__ import annotations

from datetime import date
from typing import Any, Dict, List

from . import storage
from .models import Routine


def _archive_old_recurring(tasks: List[Dict[str, Any]],
                           history: Dict[str, Any],
                           keep_from: str) -> List[Dict[str, Any]]:
    remaining: List[Dict[str, Any]] = []
    for t in tasks:
        if t.get("recurring") and t.get("created_date", "") < keep_from:
            bucket = history.setdefault(t["created_date"], {"tasks": []})
            bucket["tasks"].append({
                "id": t.get("id"),
                "title": t.get("title"),
                "category": t.get("category"),
                "priority": t.get("priority"),
                "status": t.get("status"),
                "recurring": True,
            })
        else:
            remaining.append(t)
    return remaining


def _recompute_history_totals(history: Dict[str, Any]) -> None:
    for _day, bucket in history.items():
        tasks = bucket.get("tasks", [])
        bucket["total"] = len(tasks)
        bucket["completed"] = sum(1 for t in tasks if t.get("status") == "completed")


def ensure_today(app_state: Dict[str, Any]) -> bool:
    """Ensure today's recurring tasks exist exactly once. Returns True if changed."""
    today = date.today().isoformat()
    prefs = app_state["prefs"]
    last_seen = prefs.get("last_seen_date", "")
    changed = False

    if last_seen and last_seen < today:
        app_state["tasks"] = _archive_old_recurring(
            app_state["tasks"], app_state["history"], today
        )
        _recompute_history_totals(app_state["history"])
        changed = True

    have_today = {
        t.get("routine_id")
        for t in app_state["tasks"]
        if t.get("recurring") and t.get("created_date") == today
    }
    for rdict in app_state["routines"]:
        try:
            routine = Routine.from_dict(rdict)
        except Exception:
            continue
        if not routine.active or routine.id in have_today:
            continue
        app_state["tasks"].append(routine.make_task(today).to_dict())
        changed = True

    if prefs.get("last_seen_date") != today:
        prefs["last_seen_date"] = today
        changed = True
    return changed


def reset_today_recurring(app_state: Dict[str, Any]) -> None:
    """Delete today's recurring tasks only; history & routines preserved."""
    today = date.today().isoformat()
    app_state["tasks"] = [
        t for t in app_state["tasks"]
        if not (t.get("recurring") and t.get("created_date") == today)
    ]
    ensure_today(app_state)


def persist_all(app_state: Dict[str, Any]) -> None:
    storage.save_tasks(app_state["tasks"])
    storage.save_routines(app_state["routines"])
    storage.save_history(app_state["history"])
    storage.save_prefs(app_state["prefs"])