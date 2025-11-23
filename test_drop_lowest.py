#!/usr/bin/env python3
"""
Test drop_lowest functionality
"""
from canvas.gradebook import Gradebook
from canvas.grade_processor import GradeProcessor

# Create test gradebook
gb = Gradebook()

# Problem Sets: 3 graded (scores: 50%, 80%, 90%)
assignments = [
    {"id": 1, "name": "PS1", "points_possible": 10, "assignment_group_id": 1},
    {"id": 2, "name": "PS2", "points_possible": 10, "assignment_group_id": 1},
    {"id": 3, "name": "PS3", "points_possible": 10, "assignment_group_id": 1},
]

students = [{"id": 101, "name": "Alice", "email": "alice@test.edu"}]

submissions = [
    {"user_id": 101, "assignment_id": 1, "score": 5.0},   # 50%
    {"user_id": 101, "assignment_id": 2, "score": 8.0},   # 80%
    {"user_id": 101, "assignment_id": 3, "score": 9.0},   # 90%
]

gb.load_from_data(assignments, submissions, students)

class MockGroup:
    def __init__(self, gid, name, weight):
        self.id = gid
        self.name = name
        self.group_weight = weight

groups = [MockGroup(1, "Problem Sets", 100.0)]

# Test WITHOUT drop_lowest
print("=" * 70)
print("WITHOUT drop_lowest:")
print("=" * 70)
processor1 = GradeProcessor(gradebook=gb, assignment_groups=groups)
processor1.process_grades(drop_lowest={}, only_graded=True)
for student in processor1.get_sorted_students():
    print(f"{student.name}: {student.normalized_percentage*100:.2f}%")
    print(student.format_report(partial_semester=True))

# Test WITH drop_lowest
print("\n" + "=" * 70)
print("WITH drop_lowest (drop 1):")
print("=" * 70)
processor2 = GradeProcessor(gradebook=gb, assignment_groups=groups)
processor2.process_grades(drop_lowest={"Problem Sets": 1}, only_graded=True)
for student in processor2.get_sorted_students():
    print(f"{student.name}: {student.normalized_percentage*100:.2f}%")
    print(student.format_report(partial_semester=True))

print("\n" + "=" * 70)
print("EXPECTED:")
print("=" * 70)
print("WITHOUT: (50% + 80% + 90%) / 3 = 73.33%")
print("WITH:    (80% + 90%) / 2 = 85.00% (dropped 50%)")
