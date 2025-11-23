#!/usr/bin/env python3
"""Minimal test harness for Roster class."""
from canvas.roster import Roster


def demo_basic():
    r = Roster()
    r.add_students([
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
    ])
    r.add_instructors({"id": 10, "name": "Prof. Smith"})
    r.add_tas({"id": 20, "name": "TA Tom"})
    r.add_admins({"id": 99, "name": "Admin Ann"})
    r.add_observers({"id": 300, "name": "Parent Pam"})

    print("Counts:", r.counts())
    print("Find 1:", r.find_user(1))
    print("All students:", r.get_users("students"))
    print("Serialized keys:", list(r.to_dict().keys()))


if __name__ == "__main__":
    demo_basic()
