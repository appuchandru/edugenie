"""Domain models used by EduGenie."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Note:
    """A note saved by a student."""

    id: int
    subject: str
    title: str
    content: str
    tags: list[str] = field(default_factory=list)
    created_at: str = field(
        default_factory=lambda: datetime.now().isoformat(timespec="seconds")
    )
    review_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Note":
        return cls(
            id=int(payload["id"]),
            subject=str(payload["subject"]),
            title=str(payload["title"]),
            content=str(payload["content"]),
            tags=[str(tag) for tag in payload.get("tags", [])],
            created_at=str(payload.get("created_at", "")),
            review_count=int(payload.get("review_count", 0)),
        )


@dataclass(frozen=True)
class StudySession:
    """One focused block in a study plan."""

    subject: str
    minutes: int
    objective: str


@dataclass(frozen=True)
class StudyPlan:
    """A planned set of study sessions."""

    total_minutes: int
    sessions: list[StudySession]


@dataclass(frozen=True)
class QuizQuestion:
    """A lightweight revision question derived from a note."""

    prompt: str
    answer: str
    source_title: str
    subject: str