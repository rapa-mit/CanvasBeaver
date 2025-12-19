# Interactive Email Confirmation - Quick Guide

## Overview

By default, `email_grades.py` asks for confirmation before sending each email to a student. This gives you control over the email sending process and allows you to:

- **Review** each student's details before sending
- **Skip** students if needed (e.g., incomplete grades, special cases)
- **Preview** email content before sending
- **Stop** at any point if you notice a problem
- **Continue** sending to all remaining students without further prompts

## How It Works

When you run the script normally:

```bash
python3 email_grades.py --course-id 33045
```

For each student, you'll see a prompt like this:

```
======================================================================
Student 15/57: Jane Doe
======================================================================
Email: jane@mit.edu
Report file: Jane Doe.txt
Excel file: Jane Doe.xlsx

Send email? ([y]es/[n]o/[q]uit/[p]review/[a]ll):
```

## Available Options

### `y` or `yes` or just press `Enter`
**Send email to this student**
- Sends the email immediately
- Continues to the next student
- This is the default if you just press Enter

### `n` or `no` or `s` or `skip`
**Skip this student**
- Does not send email to this student
- Continues to the next student
- Student is marked as "skipped" in the final summary

### `q` or `quit` or `exit`
**Stop sending and quit**
- Stops the email process immediately
- All remaining students are skipped
- Shows final summary with counts

### `p` or `preview`
**Preview the email content**
- Shows the first 500 characters of the email body
- Shows To, From, Subject headers
- Returns to the prompt so you can decide to send or skip
- Useful for verifying email content before sending

### `a` or `all`
**Send to all remaining students**
- Sends email to this student
- Automatically sends to ALL remaining students without further prompts
- Same as using `--no-confirm` flag from this point forward
- Useful when you've verified the first few emails and want to batch-send the rest

## Examples

### Example 1: Careful Review
Send to a few students, review each one:
```
Send email? ([y]es/[n]o/[q]uit/[p]review/[a]ll): y
✓ Sent

Student 2/57: John Smith
...
Send email? ([y]es/[n]o/[q]uit/[p]review/[a]ll): p
[Shows preview]
Send email? ([y]es/[n]o/[q]uit/[p]review/[a]ll): y
✓ Sent
```

### Example 2: Skip Problematic Students
```
Send email? ([y]es/[n]o/[q]uit/[p]review/[a]ll): y
✓ Sent

Student 2/57: Incomplete Student
...
Send email? ([y]es/[n]o/[q]uit/[p]review/[a]ll): n
SKIP: Incomplete Student

Student 3/57: Jane Doe
...
Send email? ([y]es/[n]o/[q]uit/[p]review/[a]ll): y
✓ Sent
```

### Example 3: Verify First Few, Then Batch Send
```
Send email? ([y]es/[n]o/[q]uit/[p]review/[a]ll): y
✓ Sent

Student 2/57: John Smith
...
Send email? ([y]es/[n]o/[q]uit/[p]review/[a]ll): y
✓ Sent

Student 3/57: Jane Doe
...
Send email? ([y]es/[n]o/[q]uit/[p]review/[a]ll): a
Sending to all remaining students without confirmation...
Sending to Jane Doe <jane@mit.edu>... ✓ Sent
Sending to Bob Jones <bob@mit.edu>... ✓ Sent
[continues for all remaining students]
```

### Example 4: Emergency Stop
```
Send email? ([y]es/[n]o/[q]uit/[p]review/[a]ll): y
✓ Sent

Student 2/57: John Smith
[Notice something is wrong with the grades]
Send email? ([y]es/[n]o/[q]uit/[p]review/[a]ll): q
Quitting. Remaining students will be skipped.
SKIP: Bob Jones - user cancelled
SKIP: Jane Doe - user cancelled
[all remaining students skipped]

EMAIL SUMMARY
======================================================================
Successfully sent: 1
Failed: 0
Skipped (no email/report): 55
```

## Batch Mode (No Confirmation)

If you're confident everything is correct and want to send to all students without individual prompts:

```bash
python3 email_grades.py --course-id 33045 --no-confirm
```

This will:
- Send to all students automatically
- Not ask for confirmation for each student
- Still show which student is being emailed
- Still provide a final summary

## Recommended Workflow

1. **First time**: Use interactive mode to verify first few emails
   ```bash
   # For mid-semester progress reports:
   python3 email_grades.py --course-id 33045
   
   # For final grades (end of semester):
   python3 email_grades.py --course-id 33045 --final-grades
   ```
   - Send to first 2-3 students manually
   - Use `p` to preview emails
   - If everything looks good, use `a` to send to all remaining

2. **Subsequent runs**: If you're repeating with new grade data
   ```bash
   python3 email_grades.py --course-id 33045 --no-confirm
   # Or for final grades:
   python3 email_grades.py --course-id 33045 --final-grades --no-confirm
   ```
   - Skip confirmation if you're confident everything is correct

3. **Test mode**: Always test first with yourself
   ```bash
   # Test mid-semester message:
   python3 email_grades.py --course-id 33045 --test-email your@email.com
   
   # Test final grades message:
   python3 email_grades.py --course-id 33045 --final-grades --test-email your@email.com
   ```
   - Still uses interactive confirmation
   - All emails go to your test address
   - Use this to verify email formatting before sending to students

## Final Summary

After all emails are sent (or skipped), you'll see:

```
======================================================================
EMAIL SUMMARY
======================================================================
Successfully sent: 45
Failed: 2
Skipped (no email/report): 10
Total students: 57
```

- **Successfully sent**: Emails that were sent successfully
- **Failed**: Emails that failed to send (SMTP errors, etc.)
- **Skipped**: Students you manually skipped or who had no email/report
- **Total students**: Total number of students in the course

## Tips

1. **Use preview liberally**: Press `p` to preview emails to verify formatting
2. **Start with test mode**: Always send to yourself first with `--test-email`
3. **Verify first few**: Send to 2-3 students, then use `a` for the rest
4. **Don't panic**: If something looks wrong, press `q` to quit immediately
5. **Check summary**: Review the final summary to see who was skipped

## Safety Features

- **Dry run mode**: Use `--dry-run` to see what would be sent without actually sending
- **Test email mode**: Use `--test-email` to send all emails to yourself
- **Interactive confirmation**: Default mode asks before each email
- **Quit anytime**: Press `q` to stop immediately
- **Skip students**: Press `n` to skip problematic cases

## Common Use Cases

### "I want to send to everyone except a few students"
```bash
python3 email_grades.py --course-id 33045
# Press 'y' for most students
# Press 'n' to skip the few you want to exclude
```

### "I want to verify the first 3 emails, then send to everyone else"
```bash
python3 email_grades.py --course-id 33045
# Press 'y' for first 3 students
# Press 'a' on the 4th student to send to all remaining
```

### "I want to send to everyone without any prompts"
```bash
python3 email_grades.py --course-id 33045 --no-confirm
```

### "I want to preview every email before sending"
```bash
python3 email_grades.py --course-id 33045
# For each student:
# Press 'p' to preview
# Press 'y' to send or 'n' to skip
```
