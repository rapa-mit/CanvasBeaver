# Drop Lowest Configuration Update

## Issue Fixed

The `drop_lowest` configuration was using incorrect Canvas assignment group names:
- ❌ Was using: "Homework" and "Quizzes"
- ✅ Now using: "Problem Sets" and "Quizlets"

## Updated Configuration

File: `grade_config_canvas.yaml`

```yaml
drop_lowest:
  Problem Sets: 1      # Drop lowest problem set
  Quizlets: 1          # Drop lowest quizlet
  # Midterm: 0         # Don't drop midterm (default is 0)
  # Final exam: 0      # Never drop final exam!
```

## How It Works

### Assignment Group Names
The `drop_lowest` keys MUST exactly match the Canvas assignment group names:
- Check Canvas → Settings → Assignment Groups to see the exact names
- Names are case-sensitive
- Use exact spelling and spacing

### Drop Lowest Behavior
1. **Identifies graded assignments** in each category
2. **Sorts by score** (lowest to highest)
3. **Drops the specified number** of lowest scores
4. **Recalculates average** with remaining assignments
5. **Shows dropped assignment** in the report

### Example

**Without drop_lowest:**
```
PROBLEM SETS
------------
  Problem Set #7                                  0.00%  (0.00 pts)
  Problem Set #1                                 79.00%  (3.95 pts)
  Problem Set #2                                 97.00%  (4.85 pts)
  
  Average across 3 assignment(s): 58.67%
```

**With drop_lowest (Problem Sets: 1):**
```
PROBLEM SETS
------------
  Problem Set #1                                 79.00%  (3.95 pts)
  Problem Set #2                                 97.00%  (4.85 pts)
  
  Average across 2 assignment(s): 88.00%
  ** Lowest grade dropped: Problem Set #7 (0.00%, 0.00 pts)
```

## Report Format

When a grade is dropped, the individual report shows:
```
  Average across N assignment(s): XX.XX%
  Contribution to current grade: XX.XX%
  Contribution to overall grade: XX.XX%
  ** Lowest grade dropped: Assignment Name (XX.XX%, XX.XX pts)
```

## Interaction with Partial Semester Grading

Drop lowest works seamlessly with partial semester grading:

1. **First**: Ungraded assignments are filtered out
2. **Then**: Drop lowest is applied to remaining graded assignments
3. **Finally**: Weights are recalculated and normalized

### Example Scenario

Course has:
- 13 Problem Sets (9 graded, 4 not graded)
- drop_lowest: Problem Sets: 1

Process:
1. Filter to 9 graded Problem Sets
2. Sort by score
3. Drop the lowest of the 9 graded
4. Calculate average with remaining 8
5. Show dropped assignment in report

Result:
```
Average across 8 assignment(s): 92.5%
** Lowest grade dropped: Problem Set #4 (78.75%, 3.15 pts)
```

## Testing

Run the test to verify drop_lowest works:
```bash
cd /home/rapa/courses/etc/canvas
python3 test_drop_lowest.py
```

Expected output:
- WITHOUT drop: 73.33% (average of 50%, 80%, 90%)
- WITH drop: 85.00% (average of 80%, 90%, drops 50%)

## Common Issues

### "Drop lowest not working"
**Check:**
1. Assignment group names match exactly (case-sensitive)
2. Enough graded assignments exist to drop one
3. Config file syntax is correct (YAML format)

### "Should it drop ungraded assignments?"
**No.** Drop lowest only applies to **graded** assignments:
- Ungraded assignments (all zeros) are already filtered out
- Drop lowest then applies to remaining graded work
- This prevents dropping a "real zero" vs "not yet graded"

### "Can I drop different numbers per category?"
**Yes!**
```yaml
drop_lowest:
  Problem Sets: 2      # Drop 2 lowest
  Quizlets: 1          # Drop 1 lowest
  Midterm: 0           # Drop none
```

## Configuration Examples

### Drop 1 from each category:
```yaml
drop_lowest:
  Problem Sets: 1
  Quizlets: 1
```

### Drop 2 from Problem Sets, 1 from Quizlets:
```yaml
drop_lowest:
  Problem Sets: 2
  Quizlets: 1
```

### Don't drop anything:
```yaml
drop_lowest: {}
```
or
```yaml
drop_lowest:
  Problem Sets: 0
  Quizlets: 0
```

## Verification

After running with the updated config, check individual reports:
```bash
grep "Lowest grade dropped" individual-grades/*.txt
```

Should show dropped assignments like:
```
  ** Lowest grade dropped: Problem Set #7 (0.00%, 0.00 pts)
  ** Lowest grade dropped: Quizlet #9 (0.00%, 0.00 pts)
```

If you see no output, either:
- No assignments were dropped (all high scores)
- Configuration names don't match Canvas groups
- Not enough graded assignments to drop
