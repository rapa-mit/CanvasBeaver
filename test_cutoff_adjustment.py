#!/usr/bin/env python3
"""Test script for interactive grade cutoff adjustment feature."""

from canvas.grade_processor import GradeProcessor, ProcessedStudent, GradeTypeResult, letter_grade
from canvas.gradebook import Gradebook
from dataclasses import dataclass, field
from typing import Dict

# Create mock gradebook
gb = Gradebook()

# Create mock processor with test data
class MockProcessor:
    def __init__(self):
        self.processed_students = {}
        self.letter_grade_scale = {
            0.00: 'F',
            0.61: 'D',
            0.70: 'C-',
            0.74: 'C',
            0.77: 'C+',
            0.80: 'B-',
            0.84: 'B',
            0.87: 'B+',
            0.90: 'A-',
            0.94: 'A',
            0.97: 'A+'
        }
        
        # Create test students with grades near boundaries
        test_students = [
            ("Alice", 0.965),   # A (near A+ boundary at 97%)
            ("Bob", 0.955),     # A (near A+ boundary)
            ("Carol", 0.945),   # A (at A boundary)
            ("Dave", 0.935),    # A- (near A boundary at 94%)
            ("Eve", 0.925),     # A- (near A boundary)
            ("Frank", 0.895),   # A- (near A- boundary at 90%)
            ("Grace", 0.885),   # B+ (near A- boundary)
            ("Henry", 0.875),   # B+ (at B+ boundary)
            ("Iris", 0.865),    # B (near B+ boundary at 87%)
            ("Jack", 0.835),    # B (near B boundary at 84%)
        ]
        
        for i, (name, pct) in enumerate(test_students):
            student = ProcessedStudent(
                user_id=i,
                name=name,
                normalized_percentage=pct,
                letter_grade=letter_grade(pct, self.letter_grade_scale)
            )
            self.processed_students[i] = student
    
    def get_sorted_students(self, by='name', ascending=True):
        students = list(self.processed_students.values())
        if by == 'name':
            students.sort(key=lambda s: s.name, reverse=not ascending)
        elif by == 'grade':
            students.sort(key=lambda s: s.normalized_percentage, reverse=not ascending)
        return students


# Test the function
print("Testing interactive grade cutoff adjustment")
print("=" * 70)
print("\nTest data created with students near grade boundaries:")
print()

processor = MockProcessor()

# Show initial grades
print("Initial grades:")
for student in processor.get_sorted_students(by='grade', ascending=False):
    print(f"  {student.name:15s} {student.normalized_percentage*100:6.2f}% = {student.letter_grade}")

print("\n" + "=" * 70)
print("✓ Test setup complete")
print("\nTo test interactively, run:")
print("  python3 process_grades.py --course-id <ID> --config grade_config_canvas.yaml")
print("\nThe new feature will prompt after showing grade lists:")
print("  'Would you like to review and adjust grade cutoffs? (y/N):'")
