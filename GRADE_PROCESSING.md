# Advanced Grade Processing Guide

This guide explains how to use the sophisticated grade processing system that replaces CSV-based workflows with direct Canvas API queries.

## Quick Start

1. **Create a configuration file** (e.g., `my_course_config.yaml`):

```yaml
# Use Canvas assignment group weights (recommended!)
use_canvas_groups: true

drop_lowest:
  Homework: 1     # Use exact Canvas assignment group names
  Quizzes: 1
```

2. **Run the processor**:

```bash
python3 process_grades.py --config my_course_config.yaml
```

3. **Review outputs**:
   - `grades_summary.csv` - Spreadsheet with all grades
   - `anomaly_report.txt` - Students with suspicious grade patterns
   - `individual-grades/` - Detailed per-student reports

## Configuration Reference

### use_canvas_groups (recommended)

When `true`, grade type weights are automatically retrieved from Canvas assignment groups. This is the recommended mode.

```yaml
use_canvas_groups: true
```

**Advantages:**
- No duplication of weights - single source of truth in Canvas
- Stays in sync with Canvas automatically
- Simpler configuration
- Works with Canvas's "Weighted by Group" feature

**Requirements:**
- Course must have assignment groups defined
- "Weighted by Group" should be enabled in Canvas (though not strictly required)
- Assignment group weights should be set in Canvas

### use_canvas_groups: false (legacy/manual mode)

When `false`, you manually define grade type weights in the config file. Use this if:
- Canvas doesn't have assignment group weights configured
- You want to override Canvas weights
- You're doing custom calculations

```yaml
use_canvas_groups: false

grade_types:
  Problem Set: 0.15    # 15% of final grade
  Quizlet: 0.25        # 25% of final grade
  Midterm: 0.25        # 25% of final grade
  Final: 0.35          # 35% of final grade

allow_partial: false   # Set true for mid-semester grading
```

### drop_lowest

Number of lowest assignments to drop for each assignment group. Use the **exact** assignment group names from Canvas.

```yaml
drop_lowest:
  Homework: 1       # Drop lowest homework (use exact Canvas group name)
  Quizzes: 1        # Drop lowest quiz
  # Labs: 0         # Don't drop any labs (default is 0)
  # Exams: 0        # Never drop exams!
```

**Important:** Assignment group names are case-sensitive and must exactly match Canvas group names. Run `python3 list_assignments.py` to see your Canvas assignment groups.

### allow_partial (manual mode only)

Only used when `use_canvas_groups: false`. Set to `true` for mid-semester grading when not all assignments exist yet. This allows grade type weights to sum to less than 1.0.

```yaml
use_canvas_groups: false

grade_types:
  Problem Set: 0.15
  Quizlet: 0.25
  Midterm: 0.25
  # Final: 0.35     # Not yet given

allow_partial: true
```

When `use_canvas_groups: true`, partial semester grading is handled automatically - the processor always normalizes based on completed work.

### letter_grade_scale (optional)

Path to a custom letter grade scale YAML file. If not specified, uses `MIT-letter-grades.yaml` by default.

```yaml
letter_grade_scale: MIT-letter-grades.yaml      # Default (generous)
# letter_grade_scale: strict-letter-grades.yaml  # Stricter traditional scale
# letter_grade_scale: my-custom-scale.yaml       # Your own scale
```

## Letter Grade Scales

Letter grade scales are defined in YAML files with threshold → grade mappings.

### MIT Scale (MIT-letter-grades.yaml)

Generous scale based on MIT's 5.0 grading system:
- A+ : 97%+
- A  : 94-96%
- A- : 90-93%
- B+ : 87-89%
- B  : 84-86%
- B- : 80-83%
- etc.

### Strict Scale (strict-letter-grades.yaml)

Traditional 10-point scale with 3-point subdivisions:
- A+ : 97%+
- A  : 93-96%
- A- : 90-92%
- B+ : 87-89%
- B  : 83-86%
- B- : 80-82%
- etc.

### Creating Custom Scales

Create a YAML file with this format:

```yaml
scale:
  0.00: F      # Below 60%
  0.60: D      # 60-69%
  0.70: C      # 70-79%
  0.80: B      # 80-89%
  0.90: A      # 90%+
```

**Rules:**
- Thresholds must be decimals (0.0-1.0), not percentages
- Thresholds should be in ascending order
- The grade assigned is the one for the highest threshold met or exceeded

## Anomaly Detection

The system automatically flags suspicious grade patterns that may indicate:
- Academic integrity issues
- Students who need help
- Grading errors

### Types of Anomalies Detected

1. **Large Performance Gaps**
   - High performance (>90%) in one category with >20% gap to another
   - Example: 95% on quizlets but 60% on problem sets
   - May indicate cheating or fundamental misunderstanding

2. **High Variance Within Category**
   - Standard deviation >20% within a grade type
   - Example: Alternating 100% and 40% on quizzes
   - May indicate inconsistent effort or collaboration

3. **Statistical Outliers**
   - Performance >2 standard deviations above class mean and >95%
   - Example: 98% when class average is 75%
   - May indicate exceptional performance (good!) or anomalies

### Reviewing Anomalies

Flagged students appear in:
- `anomaly_report.txt` with detailed breakdown
- Grade lists with ⚠ symbol
- Individual reports with "GRADE PATTERN ALERTS" section

**Important:** Anomalies are flags for review, not proof of issues. Investigate before taking action.

## Command-Line Options

```bash
python3 process_grades.py [OPTIONS]

Options:
  --config FILE             Configuration YAML file (required)
  --course-id ID            Canvas course ID (optional, will prompt if omitted)
  --output-dir DIR          Output directory for reports (default: current directory)
  --include-inactive        Include inactive student enrollments
```

## Output Files

### grades_summary.csv

Spreadsheet with columns:
- Name, Email, MIT ID
- One column per grade type with percentage
- Total %, Letter Grade
- Alerts (YES if anomalies detected)

Use for:
- Quick overview of all students
- Import into registrar systems
- Identifying struggling students

### anomaly_report.txt

Detailed text report with:
- List of flagged students
- Grade breakdown by type
- Specific anomalies detected

Use for:
- Investigating potential issues
- Office hours follow-up
- Academic integrity reviews

### individual-grades/*.txt

One file per student with:
- Overall grade and letter
- Breakdown by grade type
- Individual assignment scores
- Dropped assignments noted
- Anomaly alerts (if any)

Use for:
- Sharing grades with students
- Grade disputes
- Advising conversations

## Best Practices

1. **Test with small courses first** - Verify configuration works before processing large courses

2. **Review anomalies promptly** - Flags are most useful when acted on quickly

3. **Keep backups** - Save output directories with timestamps for record-keeping

4. **Use partial mode wisely** - Enable `allow_partial` during semester, disable for final grades

5. **Document your scale** - If using custom letter grades, document your reasoning

6. **Check assignment matching** - Review which assignments matched which grade types in the output

## Troubleshooting

### "Grade type not found in gradebook"

**Problem:** Configuration references a grade type pattern that doesn't match any assignments.

**Solution:** Check your `group_name_map` patterns against actual Canvas assignment names. Run `python3 list_assignments.py` to see all assignment names.

### "Grade type weights sum to X, expected 1.0"

**Problem:** Weights don't add up correctly.

**Solution:** 
- Check arithmetic in `grade_types` section
- Set `allow_partial: true` if doing mid-semester grading
- Use decimals, not percentages (0.25 not 25)

### Anomalies for good students

**Problem:** Top students flagged as anomalies.

**Solution:** Statistical outlier detection flags exceptional performance. Review the specific flags - "Statistical outlier" with high z-scores for good students is normal and can be ignored.

### Wrong letter grades

**Problem:** Letter grades don't match expectations.

**Solution:**
- Check which `letter_grade_scale` is being used
- Review the scale file thresholds
- Remember thresholds are percentages (0.0-1.0), not points

## Migration from CSV-based System

If you previously used `canvas-grades-improved.py` with CSV downloads:

1. **No CSV download needed:** Processor queries API directly for everything
2. **Use Canvas groups:** Set `use_canvas_groups: true` - no need to redefine weights!
3. **Simpler config:** Just specify drop policies and letter grade scale
4. **Test first:** Run on a test course to verify Canvas assignment groups are set up correctly
5. **Outputs:** Same format, but more automated

### Before (CSV-based):
1. Download gradebook CSV from Canvas
2. Define grade types and weights in Python
3. Map assignment name patterns to types
4. Run processor on CSV file

### After (API-based):
1. Create simple YAML config (just drop policies)
2. Run processor (it fetches everything from Canvas)
3. Done!

## Examples

- `grade_config_canvas.yaml` - Recommended: use Canvas assignment group weights
- `grade_config_example.yaml` - Legacy: manual weight configuration
