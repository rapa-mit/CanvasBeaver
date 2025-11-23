#!/usr/bin/env python3
"""
list_assignments.py
--------------------------------
Retrieve and display assignments from a Canvas course, showing assignment types/groups.

Usage:
  python3 list_assignments.py [--course-id ID]
"""
from __future__ import annotations

import argparse

from canvas.connection import CanvasConnection
from canvas.course import Course
from canvas.assignment import AssignmentManager


def main():
    parser = argparse.ArgumentParser(description="List Canvas course assignments")
    parser.add_argument("--course-id", type=int, help="Canvas course ID (optional)")
    args = parser.parse_args()

    conn = CanvasConnection()
    course = Course.from_args(conn, args.course_id)

    # Get assignments and groups
    assignment_mgr = AssignmentManager(course.canvas_course)

    # Display assignment groups
    print("\n=== Assignment Groups ===")
    groups = assignment_mgr.groups
    if not groups:
        print("  No assignment groups found.")
    else:
        for g in groups:
            weight_str = f" (weight: {g.group_weight}%)" if g.group_weight is not None else ""
            print(f"  {g.name} [id={g.id}]{weight_str}")

    # Display assignments grouped by type
    print("\n=== Assignments ===")
    assignments = assignment_mgr.assignments
    if not assignments:
        print("  No assignments found.")
    else:
        grouped = assignment_mgr.group_by_type()
        for gid in sorted(grouped.keys(), key=lambda x: x or 0):
            group, assgns = grouped[gid]
            group_name = group.name if group else (f"Group {gid}" if gid else "Ungrouped")
            print(f"\n{group_name}:")
            for a in assgns:
                pts_str = f"{a.points_possible} pts" if a.points_possible is not None else "ungraded"
                due_str = f" (due: {a.due_at[:10]})" if a.due_at else ""
                pub_str = " [unpublished]" if a.published is False else ""
                print(f"  - {a.name} [{pts_str}]{due_str}{pub_str}")


if __name__ == "__main__":
    main()
