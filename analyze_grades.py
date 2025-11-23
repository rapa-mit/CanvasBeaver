#!/usr/bin/env python3
"""
analyze_grades.py
--------------------------------
Analyze gradebook for a course: overall stats, assignment stats, and optional per-student summary.

Usage:
  python3 analyze_grades.py [--course-id ID] [--student-id UID] [--include-inactive]
"""
from __future__ import annotations

import argparse

from canvas.connection import CanvasConnection
from canvas.course import Course
from canvas.gradebook import get_course_gradebook


def main():
    parser = argparse.ArgumentParser(description="Analyze Canvas course grades")
    parser.add_argument("--course-id", type=int, help="Canvas course ID (optional)")
    parser.add_argument("--student-id", type=int, help="Specific student user ID to show details (optional)")
    parser.add_argument("--include-inactive", action="store_true", help="Include inactive enrollments")
    args = parser.parse_args()

    conn = CanvasConnection()
    course = Course.from_args(conn, args.course_id)
    gb = get_course_gradebook(conn, course.course_id, include_inactive=args.include_inactive)

    overall = gb.overall_stats()
    print("\nOverall grade stats:")
    for k in ["count", "mean", "median", "std", "min", "max"]:
        if k in overall:
            print(f"  {k}: {overall[k]}")

    # Assignment stats
    print("\nAssignment stats:")
    for a in gb.get_assignments():
        stats = gb.assignment_stats(a.id)
        m = stats.get("mean")
        print(f"  - {a.name} [id={a.id}, pts={a.points_possible}]: count={stats['count']}, mean={m}, missing={stats['missing']}, excused={stats['excused']}")

    # Top students by percent
    print("\nTop students by percent:")
    for uid, pct in gb.top_students(10):
        print(f"  - user {uid}: {pct:.2f}%")

    # Optional student detail
    if args.student_id is not None:
        s = gb.get_student(args.student_id)
        if not s:
            print(f"\nStudent {args.student_id} not found")
        else:
            print(f"\nStudent detail for {s.name or s.login or s.id} (id={s.id}):")
            pct_str = f"{s.percent:.2f}%" if s.percent is not None else "N/A"
            print(f"  Total: {s.total_score}/{s.total_points} ({pct_str})")
            for a in gb.get_assignments():
                sc = s.scores.get(a.id)
                if sc is None:
                    print(f"    - {a.name}: (no submission)")
                else:
                    flag = "excused" if sc.excused else ("missing" if sc.missing else ("late" if sc.late else ""))
                    flag = f" ({flag})" if flag else ""
                    pts = a.points_possible if a.points_possible is not None else "?"
                    print(f"    - {a.name}: {sc.score}/{pts}{flag}")


if __name__ == "__main__":
    main()
