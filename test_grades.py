#!/usr/bin/env python3
"""Synthetic test for Gradebook analytics without Canvas API access."""
from canvas.gradebook import Gradebook


def build_synthetic():
    assignments = [
        {"id": 1, "name": "HW1", "points_possible": 100},
        {"id": 2, "name": "HW2", "points_possible": 50},
    ]
    students = [
        {"id": 10, "name": "Alice"},
        {"id": 11, "name": "Bob"},
        {"id": 12, "name": "Carol"},
    ]
    submissions = [
        {"user_id": 10, "assignment_id": 1, "score": 95},
        {"user_id": 10, "assignment_id": 2, "score": 45},
        {"user_id": 11, "assignment_id": 1, "score": 80},
        {"user_id": 11, "assignment_id": 2, "score": 50},
        # Carol missing HW1, partial HW2
        {"user_id": 12, "assignment_id": 2, "score": 25},
    ]
    gb = Gradebook()
    gb.load_from_data(assignments, submissions, students)
    return gb


def test_totals():
    gb = build_synthetic()
    alice = gb.get_student(10)
    assert alice.percent is not None
    # Alice: 95 + 45 = 140 / 150 -> 93.33%
    assert round(alice.percent, 2) == 93.33

    bob = gb.get_student(11)
    # Bob: 80 + 50 = 130 / 150 -> 86.67%
    assert round(bob.percent, 2) == 86.67

    carol = gb.get_student(12)
    # Carol: only HW2 25 / (missing HW1 counts its points) -> 25 / 150 = 16.67%
    assert round(carol.percent, 2) == 16.67

    overall = gb.overall_stats()
    assert overall["count"] == 3


if __name__ == "__main__":
    test_totals()
    print("Synthetic gradebook tests passed.")
