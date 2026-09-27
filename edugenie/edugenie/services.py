"""Core EduGenie services.

The services are deliberately independent from the CLI so they can be reused by
a future web, desktop, or mobile interface.
"""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any, Iterable

from .models import Note, QuizQuestion, StudyPlan, StudySession


DEFAULT_DATA = {"next_note_id": 1, "notes": []}


class EduGenieStore:
    """Small JSON-backed store for local student data."""

    def __init__(self, path: str | Path = "data/edugenie.json") -> None:
        self.path = Path(path)

    def _read(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"next_note_id": 1, "notes": []}
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise ValueError(f"Could not read EduGenie data: {error}") from error
        return {
            "next_note_id": int(payload.get("next_note_id", 1)),
            "notes": payload.get("notes", []),
        }

    def _write(self, payload: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self.path.with_suffix(".tmp")
        temporary_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        temporary_path.replace(self.path)

    def list_notes(self, subject: str | None = None) -> list[Note]:
        notes = [Note.from_dict(item) for item in self._read()["notes"]]
        if subject:
            normalized_subject = subject.casefold()
            notes = [
                note
                for note in notes
                if note.subject.casefold() == normalized_subject
            ]
        return sorted(notes, key=lambda note: note.created_at, reverse=True)

    def add_note(
        self,
        subject: str,
        title: str,
        content: str,
        tags: Iterable[str] = (),
    ) -> Note:
        subject = subject.strip()
        title = title.strip()
        content = content.strip()
        if not subject or not title or not content:
            raise ValueError("Subject, title, and content are required.")

        payload = self._read()
        note = Note(
            id=payload["next_note_id"],
            subject=subject,
            title=title,
            content=content,
            tags=sorted(
                {tag.strip() for tag in tags if tag.strip()},
                key=str.casefold,
            ),
        )
        payload["next_note_id"] += 1
        payload["notes"].append(note.to_dict())
        self._write(payload)
        return note

    def record_review(self, note_id: int) -> Note:
        payload = self._read()
        for raw_note in payload["notes"]:
            if int(raw_note["id"]) == note_id:
                raw_note["review_count"] = int(raw_note.get("review_count", 0)) + 1
                self._write(payload)
                return Note.from_dict(raw_note)
        raise ValueError(f"No note found with id {note_id}.")

    def stats(self) -> dict[str, int]:
        notes = self.list_notes()
        subjects = {note.subject.casefold() for note in notes}
        return {
            "notes": len(notes),
            "subjects": len(subjects),
            "reviews": sum(note.review_count for note in notes),
        }


def _question_from_note(note: Note) -> QuizQuestion:
    """Turn the first sentence of a note into a recall prompt."""

    answer = note.content.strip()
    first_sentence = answer.replace("\n", " ").split(".")[0].strip()
    if len(first_sentence) > 90:
        first_sentence = f"{first_sentence[:87].rstrip()}..."
    prompt = f"What should you remember about “{note.title}”?"
    if first_sentence:
        prompt += f" Hint: {first_sentence}"
    return QuizQuestion(
        prompt=prompt,
        answer=answer,
        source_title=note.title,
        subject=note.subject,
    )


def generate_quiz(
    notes: Iterable[Note],
    count: int = 5,
    seed: int | None = None,
) -> list[QuizQuestion]:
    """Create a random quiz from notes without mutating the input."""

    if count < 1:
        raise ValueError("Quiz count must be at least 1.")
    available_notes = list(notes)
    if not available_notes:
        return []
    rng = random.Random(seed)
    rng.shuffle(available_notes)
    return [_question_from_note(note) for note in available_notes[:count]]


def build_study_plan(
    notes: Iterable[Note],
    available_minutes: int,
) -> StudyPlan:
    """Split available time across subjects with saved notes."""

    if available_minutes < 1:
        raise ValueError("Available study time must be at least 1 minute.")

    grouped: dict[str, list[Note]] = {}
    for note in notes:
        grouped.setdefault(note.subject, []).append(note)

    if not grouped:
        return StudyPlan(total_minutes=available_minutes, sessions=[])

    subjects = sorted(grouped, key=str.casefold)
    base_minutes, remainder = divmod(available_minutes, len(subjects))
    sessions: list[StudySession] = []
    for index, subject in enumerate(subjects):
        minutes = base_minutes + (1 if index < remainder else 0)
        subject_notes = grouped[subject]
        objective = f"Review {len(subject_notes)} note"
        if len(subject_notes) != 1:
            objective += "s"
        objective += " and complete a short recall quiz."
        sessions.append(
            StudySession(
                subject=subject,
                minutes=minutes,
                objective=objective,
            )
        )
    return StudyPlan(total_minutes=available_minutes, sessions=sessions)