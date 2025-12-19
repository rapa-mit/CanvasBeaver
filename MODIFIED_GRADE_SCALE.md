# Modified Letter Grade Scale Feature

## Overview

The grade processing system now supports using a **second, modified letter grade conversion table** to show alternative grades alongside the primary grades. This is useful for:

- Comparing different grading policies
- Showing "what-if" scenarios with adjusted thresholds
- Demonstrating impact of grade scale changes
- Providing alternative perspectives on student performance

## Usage

### Command Line

Add the `--modified-grade-scale` argument when running `process_grades.py`:

```bash
python3 process_grades.py \
  --course-id 33045 \
  --config grade_config_canvas.yaml \
  --modified-grade-scale test-modified-grades.yaml \
  --output-dir output-with-modified-grades
```

### Arguments

- `--modified-grade-scale PATH`: Path to a YAML file containing the modified letter grade scale
  - Uses same format as the primary letter grade scale files
  - If not specified, no modified grades are computed

## Output Changes

When a modified grade scale is specified, the following outputs are enhanced:

### 1. Console Output

The grade listing shows both the primary and modified letter grades:

```
Name                                       Score  Grade  Modified  Alert
--------------------------------------------------------------------------------
Abe Schechinger                           87.89%     B+         B       
Adeline Vining                            95.66%      A         A       
Aleksander Garbuz                         97.01%     A+         A       
```

### 2. CSV Summary Report

The CSV file includes an additional "Modified Letter Grade" column:

```csv
Name,Email,MIT ID,...,Total %,Letter Grade,Modified Letter Grade,Alerts
Abe Schechinger,abeschec@MIT.EDU,abeschec@mit.edu,...,87.89,B+,B,
```

### 3. Individual Text Reports

Each student's text report shows both grades:

```
======================================================================
CURRENT GRADE (on graded work): 87.89%
LETTER GRADE ACCORDING TO COURSE GRADING SCHEME: B+
LETTER GRADE SUBMITTED TO REGISTRAR ACCORDING TO MODIFIED CUTOFFS: B
======================================================================
```

### 4. Individual Excel Reports

Excel files include:
- **Modified Grade column** in the summary row (columns F and G)
- **ModifiedGrades sheet** with the modified conversion table
- **Formulas** that automatically compute modified grades from the percentage

The Excel formula uses: `=VLOOKUP(D6,ModifiedGrades!A:B,2,TRUE)`

## Creating a Modified Grade Scale File

Create a YAML file with the same format as existing grade scales:

```yaml
# Modified Letter Grade Scale
# ============================

scale:
  0.00: F      # Below 65%
  0.65: D      # 65-72%
  0.72: C-     # 72-75%
  0.75: C      # 75-78%
  0.78: C+     # 78-82%
  0.82: B-     # 82-85%
  0.85: B      # 85-88%
  0.88: B+     # 88-91%
  0.91: A-     # 91-95%
  0.95: A      # 95-98%
  0.98: A+     # 98%+
```

### Format Requirements

- Must have a `scale:` key at the top level
- Thresholds are decimal percentages (0.0 to 1.0)
- Thresholds must be in **ascending order**
- Each threshold maps to a letter grade string

## Example Use Cases

### 1. More Lenient Scale

Compare current grades against a more lenient scale:

```bash
python3 process_grades.py \
  --config grade_config_canvas.yaml \
  --modified-grade-scale lenient-grades.yaml
```

### 2. Stricter Scale

Show what grades would be under a stricter grading policy:

```bash
python3 process_grades.py \
  --config grade_config_canvas.yaml \
  --modified-grade-scale strict-letter-grades.yaml
```

### 3. Department Standards

Compare course grades against department-wide standards:

```bash
python3 process_grades.py \
  --config grade_config_canvas.yaml \
  --modified-grade-scale department-standards.yaml
```

## Technical Details

### Implementation

The modified grade scale is processed in parallel with the primary scale:

1. Both scales are loaded during `GradeProcessor` initialization
2. After computing the primary letter grade, the modified grade is computed using the same percentage
3. The `modified_letter_grade` field is added to `ProcessedStudent` objects
4. Reports check for the presence of modified grades and include them when available

### Backward Compatibility

- If `--modified-grade-scale` is **not** specified, the system works exactly as before
- No changes to existing reports when modified scale is not used
- All existing grade scale files remain compatible

### Performance

- Minimal performance impact: only one additional VLOOKUP per student
- Excel files include both scales as separate sheets
- No additional API calls or database queries required

## Testing

A test modified grade scale is provided: `test-modified-grades.yaml`

Run a test with:

```bash
python3 process_grades.py \
  --course-id YOUR_COURSE_ID \
  --config grade_config_canvas.yaml \
  --modified-grade-scale test-modified-grades.yaml \
  --output-dir test-modified-output
```

Then inspect:
- Console output for both grades
- `grades_summary.csv` for the modified grade column
- Individual text reports for modified grade lines
- Excel files for the ModifiedGrades sheet and modified grade formulas

## Notes

- The same numerical percentage is used for both scales
- Only the **interpretation** (letter grade) changes, not the underlying score
- Students see both grades side-by-side for comparison
- Excel formulas allow for easy manual adjustment of thresholds
