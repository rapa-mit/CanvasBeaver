#!/usr/bin/env python3
"""
course.py
--------------------------------
Course class for working with Canvas courses.
Consolidates course selection and common operations.
"""
from __future__ import annotations

from typing import Any, Optional, TYPE_CHECKING

from .connection import CanvasConnection
from .course_selector import CourseSelector

if TYPE_CHECKING:
    from .roster import Roster


class Course:
    """Wrapper for Canvas course with convenience methods."""

    def __init__(self, canvas_connection: CanvasConnection, course_id: int):
        """Initialize Course with a connection and course ID.

        Args:
            canvas_connection: Active CanvasConnection instance
            course_id: Canvas course ID
        """
        self.canvas_connection = canvas_connection
        self.course_id = course_id
        self._canvas_course: Optional[Any] = None

    @classmethod
    def from_args(cls, canvas_connection: CanvasConnection, course_id: Optional[int] = None) -> "Course":
        """Create Course from optional course_id, using interactive selection if needed.

        Args:
            canvas_connection: Active CanvasConnection instance
            course_id: Optional course ID; if None, prompts user interactively

        Returns:
            Course instance
        """
        if course_id is None:
            selector = CourseSelector(canvas_connection)
            course_id = selector.select_course_interactive()

        return cls(canvas_connection, course_id)

    @property
    def canvas_course(self) -> Any:
        """Lazy-load and return the Canvas course object."""
        if self._canvas_course is None:
            canvas = self.canvas_connection.get_canvas()
            self._canvas_course = canvas.get_course(self.course_id)
        return self._canvas_course

    @property
    def name(self) -> str:
        """Get the course name."""
        return getattr(self.canvas_course, 'name', f'Course {self.course_id}')

    def get_assignments(self) -> list:
        """Get all assignments for this course."""
        return list(self.canvas_course.get_assignments())

    def get_assignment_groups(self) -> list:
        """Get all assignment groups for this course."""
        return list(self.canvas_course.get_assignment_groups())

    def get_enrollments(self, **kwargs) -> list:
        """Get enrollments for this course."""
        return list(self.canvas_course.get_enrollments(**kwargs))

    def get_roster(self, include_inactive: bool = False) -> "Roster":
        """Get roster for this course.

        Args:
            include_inactive: Whether to include inactive enrollments

        Returns:
            Roster object populated with course participants
        """
        from .roster import Roster
        roster = Roster()
        roster.load_from_canvas(self.canvas_course, include_inactive=include_inactive)
        return roster
