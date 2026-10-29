"""JSON persistence with atomic writes, backups, and corruption recovery."""
from __future__ import annotations

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import config


def _backup(path: Path) -> None:
    """Copy an existing file into backups/ before we overwrite it."""
    if not path.exists() or path.stat().st_size == 0:
        return
    try:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        dest = config.BACKUP_DIR / f"{path.stem}.{stamp}.bak"
        shutil.copy2(path, dest)
        _prune_backups(path.stem)
    except OSError:
        pass


def _prune_backups(stem: str) -> None:
    files = sorted(
        config.BACKUP_DIR.glob(f"{stem}.*.bak"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    for old in files[config.MAX_BACKUPS:]:
        try:
            old.unlink()
        except OSError:
            pass


def safe_write_json(path: Path, data: Any) -> None:
    """Atomically write JSON with a pre-write backup."""
    _backup(path)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def _latest_backup(stem: str) -> Optional[Path]:
    files = sorted(
        config.BACKUP_DIR.glob(f"{stem}.*.bak"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return files[0] if files else None


def load_json(path: Path, default: Any) -> Any:
    """Load JSON; recover from backup or return default on corruption."""
    if not path.exists():
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
        backup = _latest_backup(path.stem)
        if backup:
            try:
                with open(backup, "r", encoding="utf-8") as f:
                    recovered = json.load(f)
                safe_write_json(path, recovered)
                return recovered
            except (json.JSONDecodeError, OSError, UnicodeDecodeError):
                pass
        try:
            broken = path.with_suffix(path.suffix + ".corrupt")
            shutil.move(str(path), str(broken))
        except OSError:
            pass
        return default


# ---------- Typed loaders / savers ----------

def load_tasks() -> List[Dict[str, Any]]:
    data = load_json(config.TASKS_FILE, [])
    return data if isinstance(data, list) else []


def save_tasks(tasks: List[Dict[str, Any]]) -> None:
    safe_write_json(config.TASKS_FILE, tasks)


def load_routines() -> List[Dict[str, Any]]:
    data = load_json(config.ROUTINES_FILE, None)
    if data is None:
        from .models import Routine
        defaults = [Routine(**r).to_dict() for r in config.DEFAULT_ROUTINES]
        save_routines(defaults)
        return defaults
    return data if isinstance(data, list) else []


def save_routines(routines: List[Dict[str, Any]]) -> None:
    safe_write_json(config.ROUTINES_FILE, routines)


def load_history() -> Dict[str, Any]:
    data = load_json(config.HISTORY_FILE, {})
    return data if isinstance(data, dict) else {}


def save_history(history: Dict[str, Any]) -> None:
    safe_write_json(config.HISTORY_FILE, history)


def load_prefs() -> Dict[str, Any]:
    data = load_json(config.PREFS_FILE, {})
    if not isinstance(data, dict):
        data = {}
    merged = dict(config.DEFAULT_PREFS)
    merged.update(data)
    return merged


def save_prefs(prefs: Dict[str, Any]) -> None:
    safe_write_json(config.PREFS_FILE, prefs)