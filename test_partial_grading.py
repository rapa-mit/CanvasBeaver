#!/usr/bin/env python3
"""
Test the partial semester grading logic
"""
from canvas.gradebook import Gradebook
from canvas.grade_processor import GradeProcessor

# Create a simple test gradebook
gb = Gradebook()

# Assignments: 2 problem sets (one graded, one not), 1 final (not graded)
assignments = [
    {"id": 1, "name": "PS1", "points_possible": 10, "assignment_group_id": 1},
    {"id": 2, "name": "PS2", "points_possible": 10, "assignment_group_id": 1},
    {"id": 3, "name": "Final", "points_possible": 100, "assignment_group_id": 2},
]

# 2 students
students = [
    {"id": 101, "name": "Alice", "email": "alice@test.edu"},
    {"id": 102, "name": "Bob", "email": "bob@test.edu"},
]

# Submissions: PS1 graded for both, PS2 and Final not graded (zeros)
submissions = [
    {"user_id": 101, "assignment_id": 1, "score": 9.0},  # Alice: 90% on PS1
    {"user_id": 101, "assignment_id": 2, "score": 0.0},  # Alice: 0% on PS2 (not graded)
    {"user_id": 101, "assignment_id": 3, "score": 0.0},  # Alice: 0% on Final (not graded)
    {"user_id": 102, "assignment_id": 1, "score": 8.0},  # Bob: 80% on PS1
    {"user_id": 102, "assignment_id": 2, "score": 0.0},  # Bob: 0% on PS2 (not graded)
    {"user_id": 102, "assignment_id": 3, "score": 0.0},  # Bob: 0% on Final (not graded)
]

gb.load_from_data(assignments, submissions, students)

# Mock assignment groups
class MockGroup:
    def __init__(self, gid, name, weight):
        self.id = gid
        self.name = name
        self.group_weight = weight

groups = [
    MockGroup(1, "Problem Sets", 40.0),  # 40%
    MockGroup(2, "Final", 60.0),  # 60%
]

# Test with only_graded=False (old behavior)
print("=" * 70)
print("OLD BEHAVIOR (including ungraded assignments):")
print("=" * 70)
processor_old = GradeProcessor(gradebook=gb, assignment_groups=groups)
processor_old.process_grades(only_graded=False)
processor_old.print_summary()

for student in processor_old.get_sorted_students(by='name'):
    print(f"{student.name}: {student.normalized_percentage*100:.2f}% = {student.letter_grade}")
    for type_name, result in student.grade_types.items():
        print(f"  {type_name}: avg={result.average_percentage*100:.2f}%, contrib={result.contribution_to_total*100:.2f}%")

# Test with only_graded=True (new behavior)
print("\n" + "=" * 70)
print("NEW BEHAVIOR (excluding ungraded assignments):")
print("=" * 70)
processor_new = GradeProcessor(gradebook=gb, assignment_groups=groups)
processor_new.process_grades(only_graded=True)
processor_new.print_summary()

for student in processor_new.get_sorted_students(by='name'):
    print(f"{student.name}: {student.normalized_percentage*100:.2f}% = {student.letter_grade}")
    for type_name, result in student.grade_types.items():
        print(f"  {type_name}: avg={result.average_percentage*100:.2f}%, contrib={result.contribution_to_total*100:.2f}%")

print("\n" + "=" * 70)
print("EXPECTED:")
print("=" * 70)
print("OLD: Alice=18%, Bob=16% (dragged down by zeros)")
print("NEW: Alice=90%, Bob=80% (based only on graded PS1)")
