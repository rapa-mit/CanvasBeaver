#!/usr/bin/env python3
"""
Diagnostic script to check which assignments have non-zero scores
"""
import sys

# Read from the individual grade file to see what's there
filename = "individual-grades/Student Example.txt"

print("Reading from:", filename)
print("\nAssignments with 0.00%:")
print("-" * 70)

with open(filename, 'r') as f:
    for line in f:
        if "0.00%" in line and "pts)" in line:
            print(line.strip())

print("\n" + "=" * 70)
print("\nTo check if lab reports are truly ungraded, we need to look at")
print("multiple students. Let's check a few more files...")
print("=" * 70)

import os
grade_files = sorted([f for f in os.listdir("individual-grades") if f.endswith(".txt")])[:5]

for gf in grade_files:
    print(f"\n{gf}:")
    with open(f"individual-grades/{gf}", 'r') as f:
        lines = f.readlines()
        for line in lines:
            if "Lab Report" in line and "0.00%" in line:
                print("  ", line.strip())
            elif "Lab Report" in line and "0.00%" not in line and "pts)" in line:
                print("  ", line.strip(), "<-- NON-ZERO")
