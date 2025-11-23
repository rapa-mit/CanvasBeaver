#!/usr/bin/env python3
"""
print_roster.py
--------------------------------
Retrieve and print roster for a given course ID or interactively selected course.

Usage:
  python3 print_roster.py [--course-id ID] [--include-inactive]
"""
from __future__ import annotations

import argparse

from canvas.connection import CanvasConnection
from canvas.course import Course


def main():
    parser = argparse.ArgumentParser(description="Print Canvas course roster")
    parser.add_argument("--course-id", type=int, help="Canvas course ID (optional)")
    parser.add_argument("--include-inactive", action="store_true", help="Include inactive enrollments")
    args = parser.parse_args()

    conn = CanvasConnection()
    course = Course.from_args(conn, args.course_id)
    roster = course.get_roster(include_inactive=args.include_inactive)

    counts = roster.counts()
    print("\nRoster counts:")
    for role, cnt in counts.items():
        print(f"  {role}: {cnt}")

    data = roster.get_all()
    print("\nRoster list:")
    for role, users in data.items():
        if not users:
            continue
        print(f"\n{role.upper()} ({len(users)}):")
        for u in users:
            name = u.get("name") or u.get("login") or f"user:{u['id']}"
            print(f"  - {name} [id={u['id']}]")


if __name__ == "__main__":
    main()
