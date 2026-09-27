"""Compatibility exports for running EduGenie from the repository root."""

from .edugenie.services import (
    EduGenieStore,
    build_study_plan,
    generate_quiz,
)

__all__ = ["EduGenieStore", "build_study_plan", "generate_quiz"]