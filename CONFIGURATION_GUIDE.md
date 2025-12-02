# Configuration Guide

Complete guide to configuring grade processing for Canvas Beaver.

## Quick Start - Three Ways to Configure

### 1. Auto-Config (Simplest - No YAML Needed!)

```bash
python3 process_grades.py --auto-config
```

**What it does:**
- ✓ Automatically fetches assignment groups from Canvas
- ✓ Automatically fetches grade weights from Canvas
- ✓ Auto-detects drop rules if configured in Canvas
- ✓ No configuration file needed
- ✓ Works immediately

**When to use:**
- First time users
- Simple grading schemes
- Canvas already has correct weights configured
- No drop_lowest rules, or they're configured in Canvas

**Limitations:**
- Cannot specify custom drop_lowest rules
- Cannot override Canvas weights
- Cannot use custom letter grade scales

---

### 2. Generate Config (Recommended for Customization)

```bash
# Interactive mode - prompts for drop_lowest values
python3 generate_config.py --interactive

# Or use shortcut from process_grades
python3 process_grades.py --generate-config

# Non-interactive - creates template to edit
python3 generate_config.py --course-id 33045
```

**What it does:**
- ✓ Scans Canvas and detects all assignment groups
- ✓ Creates YAML file with detected groups
- ✓ Optionally prompts for drop_lowest values
- ✓ Includes helpful comments and examples
- ✓ Can be edited for further customization

**Generated file example:**
```yaml
use_canvas_groups: true
drop_lowest:
  Problem Sets: 1
  Quizlets: 1
# letter_grade_scale: MIT-letter-grades.yaml
```

**When to use:**
- Need to drop lowest grades
- Want to customize configuration
- Need reproducible grading across runs
- Want to version control your grading policy

---

### 3. Manual Config (Advanced)

Create your own YAML file from scratch or use templates:
- `grade_config_canvas.yaml` - Canvas mode template
- `grade_config_example.yaml` - Manual mode template

**When to use:**
- Complex grading policies
- Override Canvas weights
- Multiple grading scenarios
- Custom letter grade scales
- Research or audit purposes

---

## Configuration File Format

### Canvas Mode (Recommended)

Pulls weights from Canvas, you specify drop rules:

```yaml
# Use Canvas Assignment Groups
use_canvas_groups: true

# Drop Lowest Grades
drop_lowest:
  Problem Sets: 1      # Drop lowest problem set
  Quizlets: 1          # Drop lowest quizlet
  # Midterm: 0         # Don't drop any (default)
  # Final exam: 0      # Never drop final exam!

# Letter Grade Scale (Optional)
letter_grade_scale: MIT-letter-grades.yaml
```

**Key points:**
- Assignment group names must **exactly** match Canvas
- Weights are fetched from Canvas automatically
- Must enable "Weighted by Group" in Canvas settings
- Can specify drop_lowest for any or all groups

---

### Manual Mode (Legacy)

Specify everything manually:

```yaml
# Manual Configuration
use_canvas_groups: false

# Grade Types and Weights
grade_types:
  Problem Sets: 0.15    # 15%
  Quizlets: 0.25        # 25%
  Midterm: 0.25         # 25%
  Final exam: 0.35      # 35%

# Drop Lowest Grades
drop_lowest:
  Problem Sets: 1
  Quizlets: 1

# Partial Semester (Optional)
allow_partial: false

# Letter Grade Scale (Optional)
letter_grade_scale: MIT-letter-grades.yaml
```

**Key points:**
- Weights must sum to 1.0 (or less if allow_partial is true)
- Assignment group names must **exactly** match Canvas
- Use for overriding Canvas weights
- More maintenance required

---

## Canvas Drop Rules Support

Canvas has built-in support for drop rules in Assignment Groups. If configured in Canvas:

**To configure in Canvas:**
1. Go to Assignments
2. Click on Assignment Group settings
3. Set "Drop" rules (e.g., "Drop lowest 1 assignment")
4. Save

**Auto-detection:**
```bash
python3 process_grades.py --auto-config
```

If Canvas has drop rules configured, they'll be automatically detected and used!

**Note:** Most courses don't configure drop rules in Canvas. That's why we support YAML configuration.

---

## Letter Grade Scales

You can customize letter grade cutoffs:

### Using Built-in Scales

**MIT Scale (default):**
- Uses MIT standard letter grade cutoffs
- File: `MIT-letter-grades.yaml`

**Strict Scale:**
- Traditional A=90%, B=80%, etc.
- File: `strict-letter-grades.yaml`

### Creating Custom Scale

Create a YAML file with grade cutoffs:

```yaml
# custom-scale.yaml
A: 93.0
A-: 90.0
B+: 87.0
B: 83.0
B-: 80.0
C+: 77.0
C: 73.0
C-: 70.0
D: 60.0
F: 0.0
```

Use it:
```yaml
letter_grade_scale: custom-scale.yaml
```

---

## Advanced Configuration

### Partial Semester Grading

For mid-semester grading where not all assignments exist yet:

**Auto-Config Mode:**
```bash
# Default behavior - only counts graded assignments
python3 process_grades.py --auto-config
```

**Manual Mode:**
```yaml
use_canvas_groups: false
grade_types:
  Problem Sets: 0.15
  Quizlets: 0.25
  Midterm: 0.25
  # Final: 0.35    # Not yet assigned
allow_partial: true
```

**Note:** By default, the system handles partial grading automatically by excluding ungraded assignments. Only use `allow_partial: true` in manual mode when weights intentionally sum to less than 1.0.

### Include Ungraded Assignments

To treat ungraded assignments as zeros:

```bash
python3 process_grades.py --auto-config --include-ungraded
```

Use at end of semester when all work should be completed.

---

## Troubleshooting

### "Course does not have 'apply_assignment_group_weights' enabled"

**Solution:** Enable in Canvas:
1. Go to Course Settings
2. Enable "Weighted Grading Periods" or "Weighted Assignment Groups"
3. Set weights for each assignment group
4. Save changes

### "Assignment group names don't match"

**Problem:** YAML uses "Quiz" but Canvas has "Quizzes"

**Solution:** Use exact names from Canvas:
```bash
# See exact names
python3 list_assignments.py --course-id XXXXX

# Or generate config to get correct names
python3 generate_config.py --interactive
```

### "Weights don't sum to 1.0"

**In Canvas Mode:** Canvas weights should sum to 100%. Check Canvas settings.

**In Manual Mode:** 
- Set `allow_partial: true` for mid-semester
- Or ensure weights sum to 1.0 (100%)

---

## Best Practices

### For Most Users
✓ Start with `--auto-config`
✓ Use `--generate-config` if you need drop rules
✓ Keep generated YAML files in version control

### For Course Administrators
✓ Configure weights in Canvas once
✓ Share generated YAML with teaching staff
✓ Document your grading policy in the YAML comments

### For Complex Grading
✓ Use manual mode with explicit weights
✓ Document reasoning in YAML comments
✓ Test with mid-semester data first

---

## Examples

### Example 1: Simple Course (No Drop Rules)
```bash
python3 process_grades.py --auto-config
```

### Example 2: Drop Lowest in Two Categories
```bash
# Generate config
python3 generate_config.py --interactive
# Answer prompts: Problem Sets=1, Quizzes=1

# Use it
python3 process_grades.py --config grade_config_16.001.yaml
```

### Example 3: Custom Letter Grades
```bash
# Create custom-grades.yaml with your cutoffs
# Generate config
python3 generate_config.py --output my-config.yaml

# Edit my-config.yaml:
# letter_grade_scale: custom-grades.yaml

# Use it
python3 process_grades.py --config my-config.yaml
```

### Example 4: Override Canvas Weights
```yaml
# my-config.yaml
use_canvas_groups: false
grade_types:
  Homework: 0.20      # Canvas says 15%, but I want 20%
  Exams: 0.80         # Canvas says 85%, but I want 80%
drop_lowest:
  Homework: 2
```

---

## See Also

- `README.md` - General usage guide
- `GRADE_PROCESSING.md` - How grade calculations work
- `PARTIAL_GRADING_GUIDE.md` - Mid-semester grading details
- Run `python3 generate_config.py --help` for more options
