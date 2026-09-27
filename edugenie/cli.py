"""Repository-level CLI entry point for EduGenie."""

from .edugenie.cli import build_parser, main

__all__ = ["build_parser", "main"]