"""
Bitwarden Organizer - Organize and structure Bitwarden JSON exports.

This package provides tools to automatically categorize, tag, and organize
Bitwarden password exports with intelligent domain analysis and safe processing.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .core import organize_bitwarden_export, OrganizerConfig

__all__ = ["organize_bitwarden_export", "OrganizerConfig"]
