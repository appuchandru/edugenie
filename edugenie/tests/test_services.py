import tempfile
import unittest
from pathlib import Path

from edugenie.models import Note
from edugenie.services import EduGenieStore, build_study_plan, generate_quiz


class EduGenieStoreTests(unittest.TestCase):
    def test_notes_round_trip_to_json(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = EduGenieStore(Path(directory) / "notes.json")
            note = store.add_note(
                "Python",
                "Decorators",
                "Decorators wrap a function and extend its behavior.",
                ["functions", "python"],
            )

            saved_notes = store.list_notes()
            self.assertEqual(len(saved_notes), 1)
            self.assertEqual(saved_notes[0].id, note.id)
            self.assertEqual(saved_notes[0].tags, ["functions", "python"])

    def test_reviews_are_recorded(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = EduGenieStore(Path(directory) / "notes.json")
            note = store.add_note("Math", "Limits", "A limit describes a value.")
            reviewed = store.record_review(note.id)
            self.assertEqual(reviewed.review_count, 1)
            self.assertEqual(store.stats()["reviews"], 1)


class StudyFeatureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.notes = [
            Note(1, "Python", "Lists", "Lists are ordered collections."),
            Note(2, "Python", "Dictionaries", "Dictionaries map keys to values."),
            Note(3, "Math", "Vectors", "Vectors have magnitude and direction."),
        ]

    def test_quiz_is_repeatable_with_seed(self) -> None:
        first = generate_quiz(self.notes, count=2, seed=7)
        second = generate_quiz(self.notes, count=2, seed=7)
        self.assertEqual(first, second)
        self.assertEqual(len(first), 2)

    def test_study_plan_distributes_minutes_across_subjects(self) -> None:
        plan = build_study_plan(self.notes, available_minutes=60)
        self.assertEqual(plan.total_minutes, 60)
        self.assertEqual(sum(session.minutes for session in plan.sessions), 60)
        self.assertEqual({session.subject for session in plan.sessions}, {"Python", "Math"})

    def test_invalid_study_time_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            build_study_plan(self.notes, available_minutes=0)


if __name__ == "__main__":
    unittest.main()