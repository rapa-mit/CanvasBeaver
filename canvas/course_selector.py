#!/usr/bin/env python3
"""
course_selector.py
--------------------------------
CourseSelector: retrieves courses and supports interactive selection.
"""
from __future__ import annotations

from datetime import datetime
import json
import os
import re
import sys
from typing import Any, List, Optional


class CourseSelector:
    """Handles course retrieval and interactive selection."""

    def __init__(self, canvas_connection, default_course_id: int = 21489, config_file: Optional[str] = None):
        """
        Initialize course selector.

        Args:
            canvas_connection: object with get_canvas() -> Canvas API client
            default_course_id: Default course ID for first-time use
            config_file: Path to session persistence file
        """
        self.canvas = canvas_connection.get_canvas()
        self.default_course_id = default_course_id
        self.config_file = config_file or os.path.join(
            os.path.dirname(__file__), ".canvas_session.json"
        )
        self.courses: List[Any] = []

    def get_active_courses(self):
        """Retrieve all active courses."""
        self.courses = [c for c in self.canvas.get_courses(
            enrollment_state='active',
            include=['term']
        )]
        return self.courses

    def get_course_year(self, course):
        """
        Extract year from course metadata.

        Tries multiple sources: start_at, term name, created_at.
        """
        try:
            # Try start_at first
            if hasattr(course, 'start_at') and course.start_at:
                dt = datetime.fromisoformat(course.start_at.replace('Z', '+00:00'))
                return dt.year

            # Try to extract from term name
            if hasattr(course, 'term') and hasattr(course.term, 'name'):
                term_name = course.term['name']
                match = re.search(r'\b(20\d{2})\b', term_name)
                if match:
                    return int(match.group(1))

            # Try created_at as fallback
            if hasattr(course, 'created_at') and course.created_at:
                dt = datetime.fromisoformat(course.created_at.replace('Z', '+00:00'))
                return dt.year
        except Exception:
            pass
        return None

    def load_last_selection(self) -> Optional[int]:
        """Load the last selected course ID from config file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    return data.get('last_course_id')
        except Exception:
            pass
        return None

    def save_selection(self, course_id: int) -> None:
        """Save the selected course ID to config file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump({'last_course_id': course_id}, f)
        except Exception:
            pass

    def display_courses(self, last_selected_id: Optional[int]) -> None:
        """Display courses in a numbered menu."""
        print("\nAvailable Canvas Courses:")
        for i, c in enumerate(self.courses, start=1):
            year = self.get_course_year(c)
            year_str = f" ({year})" if year else ""
            mark = "(last)" if (last_selected_id and c.id == last_selected_id) else ""
            print(f"  {i:2d}. {c.name}{year_str} [{c.id}] {mark}")

    def get_user_choice(self, last_selected_id: Optional[int]) -> int:
        """Prompt user for course selection."""
        try:
            choice = input("\nEnter number of course to select (press Enter for last): ").strip()
        except KeyboardInterrupt:
            print("\nCancelled.")
            sys.exit(0)

        if choice == "":
            return last_selected_id if last_selected_id is not None else self.default_course_id

        try:
            idx = int(choice) - 1
            return self.courses[idx].id
        except (ValueError, IndexError):
            print("Invalid selection. Using last selection.")
            return last_selected_id if last_selected_id is not None else self.default_course_id

    def select_course_interactive(self) -> int:
        """
        Interactive course selection workflow.

        Returns:
            Selected course ID
        """
        # Get courses
        self.get_active_courses()
        if not self.courses:
            print("No courses found.")
            sys.exit(0)

        # Load last selection
        last_selected_id = self.load_last_selection()
        if last_selected_id is None:
            last_selected_id = self.default_course_id

        # Display and get selection
        self.display_courses(last_selected_id)
        selected_course_id = self.get_user_choice(last_selected_id)

        # Confirm and save
        selected = next((c for c in self.courses if c.id == selected_course_id), None)
        if selected:
            print(f"\nSelected course: {selected.name} (ID {selected.id})")
            self.save_selection(selected_course_id)
        else:
            print(f"\nSelected course ID: {selected_course_id} (not found in list)")

        return selected_course_id
