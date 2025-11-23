#!/usr/bin/env python3
"""
list_courses.py
--------------------------------
List active Canvas courses with IDs, showing the year when available.
"""
from __future__ import annotations

from canvas.connection import CanvasConnection
from canvas.course_selector import CourseSelector


def main():
    conn = CanvasConnection()
    selector = CourseSelector(conn)
    courses = selector.get_active_courses()

    last_selected_id = selector.load_last_selection()
    selector.display_courses(last_selected_id)


if __name__ == "__main__":
    main()
