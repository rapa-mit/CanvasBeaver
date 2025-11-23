# Canvas Beaver - Partial Semester Grading Guide

## Overview

Canvas Beaver computes grades based **only on graded assignments** by default. This provides accurate "current grade" calculations that reflect students' performance on completed work, without being dragged down by unassigned or ungraded assignments.

## What Changed

### Before (Old Behavior)
- **Included ALL assignments** defined in Canvas, even if not yet assigned or graded
- Treated ungraded assignments as zeros
- Result: Everyone had artificially low grades (e.g., 44% = F)
- Example: If Final exam (60% of grade) is not graded, everyone gets 0% on it

### After (New Behavior - Default)
- **Includes ONLY graded assignments** (those with at least one non-zero score)
- Excludes ungraded/unassigned work entirely from calculations
- Recalculates weights proportionally based on graded work
- Result: Accurate current standing (e.g., 85% = B)
- Example: If Final exam is not graded, it's excluded and other categories are normalized to 100%

## How It Works

### Assignment Detection
An assignment is considered "graded" if **at least one student has a non-zero score** for it.

For example, if you have:
- Problem Set #1: Several students have scores → **GRADED**
- Problem Set #7: All students have 0.00 → **NOT GRADED** (excluded)
- Final Exam: All students have 0.00 → **NOT GRADED** (excluded)

### Weight Normalization (Simplified Approach)

The processor uses a **category-level** approach:

1. **If a category has ANY graded assignments** → Use the FULL category weight
2. **If a category has NO graded assignments** → Exclude the entire category
3. **Normalize remaining weights** to 100%

**The number of graded assignments within a category doesn't affect the weight** - only whether the category has any graded work at all.

#### Example

**Original weights:**
- Problem Sets: 15%
- Quizlets: 25%
- Midterm: 25%
- Final: 35%

**Scenario: Final not yet graded, others have graded work**

Step 1: Identify categories with graded work
- Problem Sets: ✓ Has graded assignments → Keep 15%
- Quizlets: ✓ Has graded assignments → Keep 25%
- Midterm: ✓ Has graded assignments → Keep 25%
- Final: ✗ No graded assignments → Exclude (0%)

Step 2: Sum active category weights
- Total: 15% + 25% + 25% = 65%

Step 3: Normalize to 100%
- Problem Sets: 15% ÷ 0.65 = **23.08%**
- Quizlets: 25% ÷ 0.65 = **38.46%**
- Midterm: 25% ÷ 0.65 = **38.46%**
- **Total: 100%**

Within each category, the grade is the **average of all graded assignments** in that category (after drop-lowest is applied).

## Usage

### Default (Recommended): Only Graded Assignments
```bash
export CANVAS_TOKEN="your_token_here"
python3 process_grades.py --config grade_config_canvas.yaml
```

**Note:** The `--config` argument is REQUIRED for drop_lowest to work properly.

This will:
- Identify which assignments have been graded
- Exclude ungraded assignments
- Recalculate weights proportionally
- Generate reports with "PARTIAL SEMESTER" notation

### Include All Assignments (Old Behavior)
If you want the old behavior (e.g., for end-of-semester final grades):
```bash
python3 process_grades.py --config grade_config_canvas.yaml --include-ungraded
```

## Output Changes

### Individual Reports
Reports now include a header indicating partial semester grading:

```
======================================================================
GRADE REPORT (PARTIAL SEMESTER - Based on graded assignments only)
======================================================================

Student: Alice Smith
MIT ID:  alice@mit.edu

======================================================================
CURRENT GRADE: 85.50% = B
(Based on work assigned and graded to date)
======================================================================
```

### Console Output
The processor prints information about what's being included:

```
Partial semester grading: 17 of 28 assignments have been graded

Categories with graded assignments:
  Final exam: weight = 35.0% (NO GRADED WORK - excluded)
  Midterm: weight = 25.0%
  Problem Sets: weight = 15.0%
  Quizlets: weight = 25.0%

Total weight of graded categories: 65.0%
Will normalize to 100%
```

### CSV Reports
The CSV reports show current grades based on graded work only.

## Benefits

1. **Accurate current standing**: Students see their actual performance on completed work
2. **Automatic adaptation**: As you grade more assignments, they're automatically included
3. **No manual configuration**: The system detects graded vs. ungraded automatically
4. **Transparent**: Reports clearly indicate this is partial semester grading
5. **Flexible**: Can still use old behavior with `--include-ungraded` flag

## Important Notes

### When Assignments Are Considered "Graded"
- At least ONE student must have a non-zero score
- All-zero assignments are excluded (considered not graded yet)
- Excused assignments are handled separately and don't affect detection

### Drop Lowest Still Works
Drop lowest is applied AFTER filtering to graded assignments:
- Only graded assignments in each category are considered
- Lowest is dropped from the graded set
- Category weight remains the same (full weight) as long as the category has graded work

### Anomaly Detection
Anomaly detection still works and uses only graded assignments for pattern analysis.

## Testing

A test script is provided to verify the logic:

```bash
python3 test_partial_grading.py
```

This creates a synthetic gradebook and shows the difference between old and new behavior.

## Troubleshooting

### "No config file specified" warning
- You'll see: "Warning: No config file specified, will use Canvas assignment group weights"
- This means drop_lowest won't work (no assignments will be dropped)
- Solution: Always use `--config grade_config_canvas.yaml`

### "No assignments detected as graded"
- Check that at least some students have non-zero scores
- Verify Canvas API is returning score data
- Try `--include-ungraded` to see all assignments

### "Weights don't add up to 100%"
- This is expected during partial semester
- The system automatically normalizes to 100%
- Check the console output to see the normalization

### "Student has 0% grade"
- If a student has all zeros on graded assignments, they will have 0%
- Check individual report to see which assignments are included
- Verify the student has submitted/been graded on any work

## Example Scenarios

### Scenario 1: Mid-Semester (Current)
- 9/13 Problem Sets graded
- 7/11 Quizlets graded
- Midterm graded
- Final NOT graded

**Result**: Grades normalized across 51.3% → 100% of current work

### Scenario 2: End of Semester
- All assignments graded
- Use `--include-ungraded` or default behavior works fine

**Result**: Full 100% grade calculation

### Scenario 3: First Week
- Only 1 Problem Set graded
- Everything else not graded

**Result**: Grades based entirely on that one Problem Set (100%)

## Questions?

The system is designed to be transparent and automatic. Check the console output when running to see exactly what's being included and how weights are calculated.
