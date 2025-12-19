# Final Grades Message Feature

## Overview

The email script now supports two different message templates:
1. **Mid-semester message** (default) - Includes disclaimer about progress grades
2. **Final grades message** (`--final-grades`) - For end-of-semester official final grades

## Usage

### Mid-Semester Progress Reports (Default)

```bash
python3 email_grades.py --course-id 33045
```

This uses the default message that includes:
- Statement that these are progress grades
- Disclaimer that grades may change
- Note about missing assignments and normalization

### Final Grades (End of Semester)

```bash
python3 email_grades.py --course-id 33045 --final-grades
```

This uses the final grades message that:
- States these are "final grades"
- Removes the mid-semester disclaimer
- Includes thank you message for the semester
- Presents grades as official and complete

## Message Comparison

### Mid-Semester Message

```
Dear [Student Name],

Here is your individual grade report for [Course Name].

This report shows your current standing based on graded assignments 
completed so far this semester.

I've attached an Excel spreadsheet with your grades. The spreadsheet includes:
- All your assignment scores organized by category
- Formulas showing exactly how your grade is calculated
- A "Grades" sheet with the letter grade conversion scale
- You can modify scores to see how hypothetical changes would affect your grade

If you have any questions about your grades, please don't hesitate to reach out.

Best regards

────────────────────────
IMPORTANT DISCLAIMER:

I want to clarify once again that this is just for the purpose of giving 
you an idea of how to compute your grade based on the work done so far. 
The percentage and the letter grade is not a predictor of your final 
course grade, as it's missing a large part of the grade (final 35%, 
and several ungraded or unassigned psets, labs and quizlets). The 
computation of your current grade is done by normalizing the scores you 
have obtained with the maximum score possible in all the work graded so far.
────────────────────────
```

### Final Grades Message

```
Dear [Student Name],

Here is your final grade report for [Course Name].

This report shows your final course grade based on all graded 
assignments completed this semester.

I've attached an Excel spreadsheet with your grades. The spreadsheet includes:
- All your assignment scores organized by category
- Formulas showing exactly how your grade is calculated
- A "Grades" sheet with the letter grade conversion scale
- Complete breakdown of all work completed during the semester

These are your official final grades for the course. If you have any 
questions about your final grade calculation, please don't hesitate 
to reach out.

Thank you for your hard work this semester!

Best regards
```

## Key Differences

| Aspect | Mid-Semester | Final Grades |
|--------|--------------|--------------|
| **Opening** | "individual grade report" | "final grade report" |
| **Description** | "current standing...so far" | "final course grade" |
| **Excel Notes** | "hypothetical changes" | "complete breakdown" |
| **Disclaimer** | Long disclaimer about normalization | None |
| **Closing** | "If you have questions..." | "official final grades" + thank you |
| **Tone** | Progress report, subject to change | Official, complete, final |

## Complete Examples

### Example 1: Mid-Semester With All Options

```bash
python3 email_grades.py \
  --course-id 33045 \
  --subject "Midterm Progress Report" \
  --reports-dir 16.001-2025-11-15/individual-grades
```

### Example 2: Final Grades With All Options

```bash
python3 email_grades.py \
  --course-id 33045 \
  --final-grades \
  --subject "Final Grade Report" \
  --reports-dir 16.001-2025-12-18/individual-grades \
  --no-confirm
```

### Example 3: Test Final Grades Message

```bash
python3 email_grades.py \
  --course-id 33045 \
  --final-grades \
  --test-email your@email.com
```

### Example 4: Dry Run Final Grades

```bash
python3 email_grades.py \
  --course-id 33045 \
  --final-grades \
  --dry-run
```

## When to Use Each Message

### Use Mid-Semester Message When:
- Sending progress reports during the semester
- Not all assignments are complete
- Grades might still change
- Students need to know what work is missing
- Encouraging students to improve

### Use Final Grades Message When:
- Semester is complete
- All assignments have been graded
- Grades are official and won't change
- No more work can be submitted
- End-of-semester grade distribution

## Workflow for Final Grades

1. **Process final grades** with all assignments included:
   ```bash
   python3 process_grades.py \
     --config grade_config_canvas.yaml \
     --include-ungraded  # Include all assignments
   ```

2. **Review grades** in the output directory:
   ```bash
   cat 16.001-2025-12-18/grades_summary.csv
   ```

3. **Test final grades email** to yourself:
   ```bash
   python3 email_grades.py \
     --course-id 33045 \
     --final-grades \
     --test-email your@email.com
   ```

4. **Send final grades** to all students:
   ```bash
   python3 email_grades.py \
     --course-id 33045 \
     --final-grades
   ```
   
   Review first few with interactive confirmation, then use `a` to send to all remaining.

## Customization

To further customize the messages, edit the email body templates in `email_grades.py` around line 606:

```python
if args.final_grades:
    # Final grades message
    body = f"""Dear {student.name},
    
    [Your custom final grades message here]
    """
else:
    # Mid-semester message
    body = f"""Dear {student.name},
    
    [Your custom mid-semester message here]
    """
```

## Tips

1. **Subject Line**: Consider updating the subject line for final grades:
   ```bash
   --subject "Final Course Grade Report"
   ```

2. **Test First**: Always test with `--test-email` before sending finals:
   ```bash
   python3 email_grades.py --course-id 33045 --final-grades --test-email your@email.com
   ```

3. **Dry Run**: Use `--dry-run` to verify everything looks correct:
   ```bash
   python3 email_grades.py --course-id 33045 --final-grades --dry-run
   ```

4. **Interactive Mode**: Use default interactive mode to review first few:
   - Verify message looks correct
   - Check student names and emails
   - Preview email with `p` option
   - Use `a` to send remaining after verification

5. **Timing**: Send final grades emails after:
   - All grades are entered in Canvas
   - Grade reports have been generated with `--include-ungraded`
   - You've verified grade calculations
   - Official grades are ready to be released

## Common Scenarios

### Scenario 1: Sending Final Grades at End of Semester

```bash
# 1. Process grades with all assignments
python3 process_grades.py --config grade_config_canvas.yaml --include-ungraded

# 2. Test email to yourself
python3 email_grades.py --course-id 33045 --final-grades --test-email your@email.com

# 3. Send to all (interactive confirmation)
python3 email_grades.py --course-id 33045 --final-grades
```

### Scenario 2: Sending Mid-Semester Progress Report

```bash
# 1. Process grades (only graded work)
python3 process_grades.py --config grade_config_canvas.yaml

# 2. Send to all with default message
python3 email_grades.py --course-id 33045
```

### Scenario 3: Sending Modified Final Grades

If you need to send updated final grades:

```bash
# 1. Reprocess grades
python3 process_grades.py --config grade_config_canvas.yaml --include-ungraded --no-cache

# 2. Send with updated subject
python3 email_grades.py \
  --course-id 33045 \
  --final-grades \
  --subject "Updated Final Grade Report"
```

## Technical Details

### Implementation

The `--final-grades` flag is a boolean argument that:
1. Changes the email body template
2. Removes the mid-semester disclaimer
3. Updates language from "progress" to "final"
4. Adds thank you message

### Code Location

The email body generation is in `email_grades.py` starting around line 606.

### Backward Compatibility

- Default behavior (no flag) uses mid-semester message
- Existing scripts continue to work unchanged
- `--final-grades` is optional and explicit

## Notes

- The flag only changes the email message text
- Grade calculations remain the same
- Report files (text and Excel) are unchanged
- All other email options work with `--final-grades`
- Can combine with `--no-confirm`, `--test-email`, `--dry-run`, etc.
