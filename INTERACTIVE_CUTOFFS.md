# Interactive Grade Cutoff Adjustment

## Overview

The interactive grade cutoff adjustment feature allows instructors to review students near grade boundaries and adjust letter grade cutoffs to better reflect student performance and course-specific considerations.

## How It Works

After processing grades, the system can present each grade boundary one at a time, showing:
- The current cutoff percentage
- Students slightly below the cutoff (who would get the lower grade)
- Students slightly above the cutoff (who are getting the higher grade)

For each boundary, you can:
- Keep the existing cutoff (press Enter)
- Set a new cutoff percentage (type a number like `93.5`)

The system validates all inputs to ensure cutoffs remain in proper order.

## Usage

### Option 1: Command Line Flag

Run `process_grades.py` with the `--interactive-cutoffs` flag:

```bash
python3 process_grades.py --config grade_config_canvas.yaml --interactive-cutoffs
```

This will automatically enter interactive mode after displaying initial grade distributions.

### Option 2: Interactive Prompt

Run `process_grades.py` normally:

```bash
python3 process_grades.py --config grade_config_canvas.yaml
```

After viewing the grade lists, you'll see:

```
Tip: Use --interactive-cutoffs to review and adjust grade boundaries
Would you like to review grade cutoffs now? (y/N):
```

Type `y` or `yes` to enter interactive mode.

## Example Session

```
======================================================================
INTERACTIVE GRADE CUTOFF ADJUSTMENT
======================================================================
Review students near grade boundaries and optionally adjust cutoffs.

──────────────────────────────────────────────────────────────────────
Grade Boundary: A- → A
Current cutoff: 94.00%
──────────────────────────────────────────────────────────────────────

Students BELOW cutoff (would get A-):
  Alice Smith                              93.75%
  Bob Johnson                              93.50%
  Carol Davis                              93.25%

Students ABOVE cutoff (getting A):
  Dave Wilson                              94.15%
  Eve Martinez                             94.00%

Adjust cutoff for A? (Enter new percentage or press Enter to keep 94.00%): 93.5

  ✓ Updated A cutoff: 94.00% → 93.50%
  → 2 student(s) will move from A- to A
```

## Features

### Smart Boundary Detection

The system automatically identifies students within 2% of each grade boundary, making it easy to spot borderline cases.

### Validation

All cutoff adjustments are validated to ensure:
- New cutoffs don't overlap with adjacent grade boundaries
- The scale remains properly ordered
- Values are within valid percentage ranges (0-100)

### Impact Preview

When you adjust a cutoff, the system immediately shows which students will be affected by the change.

### Automatic Recomputation

After all adjustments are made:
- Letter grades are automatically recomputed for all students
- Updated grade lists are displayed
- Summary statistics are recalculated

## Use Cases

### End of Semester Grading

Review borderline students before finalizing grades:
- Identify students just missing a grade threshold
- Adjust cutoffs based on overall course performance
- Consider special circumstances or trends

### Partial Semester Checkpoints

During mid-semester reviews:
- See how current grading scale affects student distribution
- Adjust expectations based on assignment difficulty
- Provide early warnings to struggling students

### Custom Grade Scales

Adapt the grading scale to:
- Course-specific difficulty levels
- Department or institutional standards
- Historical grade distributions

## Technical Details

### Grade Scale Format

The system uses the letter grade scale from `MIT-letter-grades.yaml` or any custom scale specified in your configuration. The scale is a dictionary mapping percentage thresholds to letter grades:

```yaml
scale:
  0.00: F
  0.61: D
  0.70: C-
  0.74: C
  0.77: C+
  0.80: B-
  0.84: B
  0.87: B+
  0.90: A-
  0.94: A
  0.97: A+
```

### Persistence

Adjusted cutoffs are used for:
- All generated reports (CSV, text, Excel)
- Individual student grade sheets
- Summary statistics

However, adjusted cutoffs are NOT saved back to the YAML file. To make permanent changes, manually edit your grade scale file.

### Margin of Interest

The system shows students within 2% (0.02) of each boundary. This margin is configurable in the code:

```python
margin = 0.02  # Show students within 2% of boundary
```

## Best Practices

1. **Review Initial Distribution**: Always look at the complete grade distribution before making adjustments

2. **Consider the Whole Class**: Adjust cutoffs based on overall performance patterns, not individual cases

3. **Document Decisions**: Keep notes on why you adjusted specific cutoffs for future reference

4. **Be Consistent**: Apply similar reasoning across all grade boundaries

5. **Test First**: Run the interactive adjustment in a test/preview mode before finalizing grades

## Limitations

- Cutoffs must be adjusted one boundary at a time (prevents accidental large-scale changes)
- Adjustments are not automatically saved to configuration files
- The 2% margin is fixed (though this could be made configurable)

## See Also

- [GRADE_PROCESSING.md](GRADE_PROCESSING.md) - General grade processing guide
- [MIT-letter-grades.yaml](MIT-letter-grades.yaml) - Default grade scale
- [CONFIGURATION_GUIDE.md](CONFIGURATION_GUIDE.md) - Configuration options
