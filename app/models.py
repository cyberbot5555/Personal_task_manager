"""Task and Routine data models with JSON (de)serialization."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field, asdict
from datetime import date
from typing import Any, Dict, Optional


def new_id() -> str:
    return uuid.uuid4().hex


@dataclass
class Task:
    title: str
    category: str = "General"
    priority: str = "Medium"
    description: str = ""
    due_date: str = ""
    due_time: str = ""
    reminder: str = ""
    status: str = "pending"
    recurring: bool = False
    routine_id: Optional[str] = None
    created_date: str = field(default_factory=lambda: date.today().isoformat())
    completed_date: str = ""
    id: str = field(default_factory=new_id)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Task":
        allowed = {f for f in cls.__dataclass_fields__}
        clean = {k: v for k, v in d.items() if k in allowed}
        clean.setdefault("title", "Untitled")
        return cls(**clean)

    def is_overdue(self, today: Optional[date] = None) -> bool:
        if self.status == "completed" or not self.due_date:
            return False
        today = today or date.today()
        try:
            y, m, d = (int(x) for x in self.due_date.split("-"))
            return date(y, m, d) < today
        except (ValueError, TypeError):
            return False


@dataclass
class Routine:
    title: str
    category: str = "General"
    priority: str = "Medium"
    description: str = ""
    reminder: str = ""
    active: bool = True
    created_date: str = field(default_factory=lambda: date.today().isoformat())
    id: str = field(default_factory=new_id)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Routine":
        allowed = {f for f in cls.__dataclass_fields__}
        clean = {k: v for k, v in d.items() if k in allowed}
        clean.setdefault("title", "Untitled Routine")
        return cls(**clean)

    def make_task(self, for_date: str) -> Task:
        return Task(
            title=self.title,
            category=self.category,
            priority=self.priority,
            description=self.description,
            reminder=self.reminder,
            status="pending",
            recurring=True,
            routine_id=self.id,
            created_date=for_date,
        )