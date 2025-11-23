#!/usr/bin/env python3
"""
canvas.py
--------------------------------
CLI entrypoint using extracted modules for Canvas LMS interactions.
Provides interactive course selection and optional roster summary.
"""

import sys
from canvas.connection import CanvasConnection
from canvas.course import Course


def main():
    """Main entry point for interactive course selection."""
    try:
        # Initialize connection and get course
        connection = CanvasConnection()
        course = Course.from_args(connection)

        # Fetch and display roster
        try:
            roster = course.get_roster()
            counts = roster.counts()
            print("\nRoster counts:")
            for role, cnt in counts.items():
                print(f"  {role}: {cnt}")
        except Exception as e:
            # Roster fetch is optional; continue if not available
            print(f"\nNote: Could not fetch roster ({e})")

    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
