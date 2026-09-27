"""Command-line interface for EduGenie."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .models import Note
from .services import EduGenieStore, build_study_plan, generate_quiz


DEFAULT_STORE = Path(__file__).resolve().parents[1] / "data" / "edugenie.json"


def _store_from_args(args: argparse.Namespace) -> EduGenieStore:
    return EduGenieStore(args.data_file or DEFAULT_STORE)


def _add_note_command(args: argparse.Namespace) -> None:
    store = _store_from_args(args)
    note = store.add_note(
        subject=args.subject,
        title=args.title,
        content=args.content,
        tags=args.tags.split(",") if args.tags else (),
    )
    print(f"Saved note #{note.id}: {note.title} ({note.subject})")


def _notes_command(args: argparse.Namespace) -> None:
    notes = _store_from_args(args).list_notes(args.subject)
    if not notes:
        print("No notes found. Add one with the 'add-note' command.")
        return
    for note in notes:
        tags = f" · tags: {', '.join(note.tags)}" if note.tags else ""
        print(f"\n#{note.id} {note.title} [{note.subject}]{tags}")
        print(f"  {note.content}")
        print(f"  Reviews: {note.review_count}")


def _quiz_command(args: argparse.Namespace) -> None:
    store = _store_from_args(args)
    questions = generate_quiz(
        store.list_notes(args.subject),
        count=args.count,
        seed=args.seed,
    )
    if not questions:
        print("Add notes before starting a quiz.")
        return

    print(f"EduGenie quiz · {len(questions)} question(s)\n")
    for index, question in enumerate(questions, start=1):
        print(f"{index}. {question.prompt}")
        input("   Press Enter to reveal the answer...")
        print(f"   Answer: {question.answer}\n")
        source_note = next(
            note
            for note in store.list_notes(question.subject)
            if note.title == question.source_title
        )
        store.record_review(source_note.id)


def _plan_command(args: argparse.Namespace) -> None:
    store = _store_from_args(args)
    plan = build_study_plan(store.list_notes(), args.minutes)
    if not plan.sessions:
        print("Add notes first so EduGenie can build a subject-based plan.")
        return
    print(f"Study plan · {plan.total_minutes} minutes\n")
    for index, session in enumerate(plan.sessions, start=1):
        print(
            f"{index}. {session.subject} · {session.minutes} minutes\n"
            f"   {session.objective}"
        )


def _stats_command(args: argparse.Namespace) -> None:
    stats = _store_from_args(args).stats()
    print(
        "EduGenie progress\n"
        f"Notes: {stats['notes']}\n"
        f"Subjects: {stats['subjects']}\n"
        f"Reviews completed: {stats['reviews']}"
    )


def _demo_command(args: argparse.Namespace) -> None:
    store = _store_from_args(args)
    if store.list_notes():
        print("Demo data already exists in this data file.")
        return
    demo_notes = [
        (
            "Data Structures",
            "Binary Trees",
            "A binary tree is a hierarchical structure where each node has at most two children.",
            "trees,algorithms",
        ),
        (
            "Operating Systems",
            "Process Scheduling",
            "Round-robin scheduling gives each ready process a fixed time slice in rotation.",
            "processes,scheduling",
        ),
        (
            "Database Systems",
            "Normalization",
            "Normalization organizes relational tables to reduce redundancy and update anomalies.",
            "sql,design",
        ),
    ]
    for subject, title, content, tags in demo_notes:
        store.add_note(subject, title, content, tags.split(","))
    print("Added three demo notes. Try: python -m edugenie quiz")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="edugenie",
        description="A local study companion for college students.",
    )
    parser.add_argument(
        "--data-file",
        type=Path,
        help="Optional path to a custom JSON data file.",
    )
    subparsers = parser.add_subparsers(dest="command")

    add_note = subparsers.add_parser("add-note", help="Save a study note.")
    add_note.add_argument("--subject", required=True)
    add_note.add_argument("--title", required=True)
    add_note.add_argument("--content", required=True)
    add_note.add_argument("--tags", help="Comma-separated tags.")
    add_note.set_defaults(handler=_add_note_command)

    notes = subparsers.add_parser("notes", help="List saved notes.")
    notes.add_argument("--subject")
    notes.set_defaults(handler=_notes_command)

    quiz = subparsers.add_parser("quiz", help="Start a revision quiz.")
    quiz.add_argument("--subject")
    quiz.add_argument("--count", type=int, default=5)
    quiz.add_argument("--seed", type=int, help="Use a repeatable question order.")
    quiz.set_defaults(handler=_quiz_command)

    plan = subparsers.add_parser("plan", help="Build a study plan.")
    plan.add_argument("--minutes", type=int, default=60)
    plan.set_defaults(handler=_plan_command)

    demo = subparsers.add_parser("demo", help="Add sample college notes.")
    demo.set_defaults(handler=_demo_command)

    stats = subparsers.add_parser("stats", help="Show progress statistics.")
    stats.set_defaults(handler=_stats_command)
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "command", None):
        parser.print_help()
        print("\nQuick start: python -m edugenie demo && python -m edugenie quiz")
        return
    try:
        args.handler(args)
    except (ValueError, OSError) as error:
        print(f"EduGenie error: {error}", file=sys.stderr)
        raise SystemExit(1) from error