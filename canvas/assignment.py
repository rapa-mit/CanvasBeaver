#!/usr/bin/env python3
"""
assignment.py
--------------------------------
Assignment and AssignmentGroup classes for working with Canvas assignments.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class AssignmentGroup:
    """Represents an assignment group (category/type)."""
    id: int
    name: str
    position: Optional[int] = None
    group_weight: Optional[float] = None

    @classmethod
    def from_canvas(cls, canvas_group: Any) -> "AssignmentGroup":
        """Create AssignmentGroup from Canvas API object."""
        return cls(
            id=canvas_group.id,
            name=canvas_group.name,
            position=getattr(canvas_group, 'position', None),
            group_weight=getattr(canvas_group, 'group_weight', None),
        )


@dataclass
class Assignment:
    """Represents an assignment with key metadata."""
    id: int
    name: str
    assignment_group_id: Optional[int] = None
    points_possible: Optional[float] = None
    due_at: Optional[str] = None
    published: Optional[bool] = None
    submission_types: Optional[List[str]] = None

    @classmethod
    def from_canvas(cls, canvas_assignment: Any) -> "Assignment":
        """Create Assignment from Canvas API object."""
        return cls(
            id=canvas_assignment.id,
            name=canvas_assignment.name,
            assignment_group_id=getattr(canvas_assignment, 'assignment_group_id', None),
            points_possible=getattr(canvas_assignment, 'points_possible', None),
            due_at=getattr(canvas_assignment, 'due_at', None),
            published=getattr(canvas_assignment, 'published', None),
            submission_types=getattr(canvas_assignment, 'submission_types', None),
        )


class AssignmentManager:
    """Manages assignments and assignment groups for a course."""

    def __init__(self, course: Any):
        """Initialize with a Canvas course object.

        Args:
            course: Canvas course object (from course_service.Course.canvas_course)
        """
        self.course = course
        self._groups: Optional[List[AssignmentGroup]] = None
        self._assignments: Optional[List[Assignment]] = None

    @property
    def groups(self) -> List[AssignmentGroup]:
        """Lazy-load and return assignment groups."""
        if self._groups is None:
            try:
                self._groups = [
                    AssignmentGroup.from_canvas(g)
                    for g in self.course.get_assignment_groups()
                ]
            except Exception:
                self._groups = []
        return self._groups

    @property
    def assignments(self) -> List[Assignment]:
        """Lazy-load and return assignments."""
        if self._assignments is None:
            try:
                self._assignments = [
                    Assignment.from_canvas(a)
                    for a in self.course.get_assignments()
                ]
            except Exception:
                self._assignments = []
        return self._assignments

    def group_by_type(self) -> Dict[Optional[int], tuple[Optional[AssignmentGroup], List[Assignment]]]:
        """Group assignments by their assignment group.

        Returns:
            Dict mapping group_id to (group_object, [assignments])
            None key holds ungrouped assignments
        """
        group_map = {g.id: g for g in self.groups}
        by_group: Dict[Optional[int], List[Assignment]] = {}

        for a in self.assignments:
            gid = a.assignment_group_id
            if gid not in by_group:
                by_group[gid] = []
            by_group[gid].append(a)

        result = {}
        for gid, assgns in by_group.items():
            result[gid] = (group_map.get(gid), assgns)

        return result

    def get_group_by_id(self, group_id: int) -> Optional[AssignmentGroup]:
        """Get assignment group by ID."""
        for g in self.groups:
            if g.id == group_id:
                return g
        return None

    def get_assignment_by_id(self, assignment_id: int) -> Optional[Assignment]:
        """Get assignment by ID."""
        for a in self.assignments:
            if a.id == assignment_id:
                return a
        return None
