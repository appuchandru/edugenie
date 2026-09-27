"""EduGenie: a local study companion for college students."""

from .models import Note, StudyPlan, StudySession
from .services import EduGenieStore, build_study_plan, generate_quiz

__all__ = [
    "EduGenieStore",
    "Note",
    "StudyPlan",
    "StudySession",
    "build_study_plan",
    "generate_quiz",
]

__version__ = "0.1.0"