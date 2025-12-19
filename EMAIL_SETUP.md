# Canvas Beaver - Email Grade Reports Setup

## Overview

Canvas Beaver's email system sends individual grade reports to students via email. It retrieves student email addresses from the Canvas API and attaches their personalized grade report files with interactive Excel spreadsheets.

## Prerequisites

1. **Run grade processing first** to generate individual reports:
   ```bash
   python3 process_grades.py --config grade_config_canvas.yaml
   ```
   This creates individual grade files in `individual-grades/` directory.

2. **SMTP server access** - You need access to an email server to send emails.

## Configuration

### Email Settings (Edit CONFIG in Script)

**The easiest way to configure email is to edit the `CONFIG` dictionary at the top of `email_grades.py` (around line 40).**

Open the script and modify these values:

```python
CONFIG = {
    'EMAIL_FROM': 'your.email@example.com',        # Your email address (sender)
    'SMTP_SERVER': 'smtp.example.com',             # SMTP server hostname
    'SMTP_PORT': 587,                               # SMTP port (587 for TLS)
    'SMTP_USE_TLS': True,                           # Use TLS encryption
    'SMTP_USER': None,                              # SMTP username (or None)
    'SMTP_PASSWORD': None,                          # SMTP password (or None)
    'EMAIL_SUBJECT': 'Your Course Grade Report',    # Email subject line
}
```

### Common SMTP Configurations

The script includes commented examples you can uncomment and modify:

**Gmail:**
```python
CONFIG = {
    'EMAIL_FROM': 'your.email@gmail.com',
    'SMTP_SERVER': 'smtp.gmail.com',
    'SMTP_PORT': 587,
    'SMTP_USE_TLS': True,
    'SMTP_USER': 'your.email@gmail.com',
    'SMTP_PASSWORD': 'your-app-password',  # Use App Password, not regular password!
    'EMAIL_SUBJECT': 'Your Course Grade Report',
}
```

**MIT (with password authentication):**
```python
CONFIG = {
    'EMAIL_FROM': 'yourname@mit.edu',
    'SMTP_SERVER': 'outgoing.mit.edu',
    'SMTP_PORT': 465,  # Use 465 for SSL/TLS (not 587)
    'SMTP_USE_TLS': True,
    'SMTP_USER': 'your-username',  # Your MIT username (e.g., 'rapa')
    'SMTP_PASSWORD': None,  # Leave None to be prompted at runtime (more secure!)
    'EMAIL_SUBJECT': 'Your Course Grade Report',
}
```
**Important**: 
- Use port **465** with SSL/TLS for authenticated SMTP at MIT (same as Thunderbird settings)
- Leave `SMTP_PASSWORD` as `None` to be prompted for password when you run the script (recommended for security)

**Local/University SMTP:**
```python
CONFIG = {
    'EMAIL_FROM': 'professor@university.edu',
    'SMTP_SERVER': 'localhost',
    'SMTP_PORT': 25,
    'SMTP_USE_TLS': False,
    'SMTP_USER': None,
    'SMTP_PASSWORD': None,
    'EMAIL_SUBJECT': 'Your Course Grade Report',
}
```

### Alternative: Environment Variables

You can still use environment variables to override the CONFIG settings:

```bash
export EMAIL_FROM="your.email@example.com"
export SMTP_SERVER="smtp.example.com"
export SMTP_PORT="587"
export SMTP_USER="your.username"
export SMTP_PASSWORD="your.password"
export SMTP_USE_TLS="true"
```

## Usage

### Quick Start

1. **Edit the CONFIG section** in `email_grades.py` with your email settings
2. **Test your email configuration**:
   ```bash
   python3 email_grades.py --test-config
   ```
   This will send a test email to verify your SMTP settings work correctly.
3. **Run with dry-run** to preview what will be sent:
   ```bash
   python3 email_grades.py --course-id 33045 --dry-run
   ```
4. **Send for real** when ready:
   ```bash
   python3 email_grades.py --course-id 33045
   ```
   The script will offer to test your email configuration before sending.

### Basic Usage

```bash
python3 email_grades.py --course-id 33045
```

### Test Email Configuration

```bash
python3 email_grades.py --test-config
```

Tests your SMTP configuration by sending a test email. You'll be prompted for a recipient address. This verifies your email settings work before processing grades.

### Dry Run (Test Without Sending)

```bash
python3 email_grades.py --course-id 33045 --dry-run
```

This shows what would be sent without actually sending emails. Good for verifying student list and report files.

### Test Mode (Send All to One Address)

```bash
python3 email_grades.py --course-id 33045 --test-email your.email@example.com
```

Sends all emails to the specified test address instead of to students. Great for testing the actual email delivery and formatting.

### Interactive Confirmation (Default)

**By default, the script will ask for confirmation before sending each email:**

```bash
python3 email_grades.py --course-id 33045
```

For each student, you'll be prompted with options:
- **`[y]es`** - Send email to this student (or just press Enter)
- **`[n]o`** - Skip this student
- **`[q]uit`** - Stop sending and skip all remaining students
- **`[p]review`** - Show preview of email content
- **`[a]ll`** - Send to this and all remaining students without further prompts

### No Confirmation Mode

To send all emails without individual confirmation prompts:

```bash
python3 email_grades.py --course-id 33045 --no-confirm
```

This is useful for batch processing when you've already verified everything is correct.

### Final Grades Message

**By default, emails include a disclaimer that grades are based on work completed so far.**

For end-of-semester final grades, use the `--final-grades` flag:

```bash
python3 email_grades.py --course-id 33045 --final-grades
```

This changes the email to:
- State these are "final grades" instead of "current standing"
- Remove the mid-semester disclaimer
- Include a thank you message for the semester

### Custom Subject Line

```bash
python3 email_grades.py --course-id 33045 --subject "Final Grade Report"
```

### Command Line Options (Override CONFIG)

You can override CONFIG settings via command line:

```bash
python3 email_grades.py \
  --course-id 33045 \
  --from-email professor@university.edu \
  --smtp-server smtp.university.edu \
  --smtp-port 587 \
  --smtp-user professor \
  --smtp-password mypassword
```

## Workflow

Recommended workflow for sending grade emails:

1. **Configure email settings** - Edit the CONFIG dictionary in `email_grades.py`

2. **Test email configuration**:
   ```bash
   python3 email_grades.py --test-config
   ```
   Send a test email to yourself to verify SMTP settings work.

3. **Process grades** to generate individual reports:
   ```bash
   python3 process_grades.py --config grade_config_canvas.yaml
   ```

4. **Test with dry run** to verify everything looks correct:
   ```bash
   python3 email_grades.py --course-id 33045 --dry-run
   ```

5. **Send to yourself** to verify email formatting and delivery with actual grade report:
   ```bash
   python3 email_grades.py --course-id 33045 --test-email your.email@example.com
   ```

6. **Send to all students** when ready:
   
   **For mid-semester progress reports:**
   ```bash
   python3 email_grades.py --course-id 33045
   ```
   
   **For end-of-semester final grades:**
   ```bash
   python3 email_grades.py --course-id 33045 --final-grades
   ```
   
   The script will offer to test your configuration one more time before sending.
   
   **By default, you'll be asked to confirm each email individually**, allowing you to:
   - Skip problematic students
   - Preview emails before sending
   - Stop at any point if something looks wrong
   
   To skip individual confirmations and send to everyone at once:
   ```bash
   python3 email_grades.py --course-id 33045 --final-grades --no-confirm
   ```

## Features

- **Email configuration testing**: Test SMTP settings before sending to students
- **Automatic email retrieval**: Gets student emails from Canvas API
- **Caching support**: Uses cached gradebook data to avoid repeated API calls
- **Dual attachments**: Attaches both text report and Excel spreadsheet to each email
- **Inlined reports**: Full text report included in email body
- **Interactive confirmation**: Prompts for each student with preview option (default)
- **Batch mode**: Use `--no-confirm` to send all without individual prompts
- **Error handling**: Continues sending even if some emails fail
- **Summary report**: Shows success/failure statistics at the end
- **Safe testing**: Dry-run and test modes prevent accidental sends
- **Password caching**: Securely caches SMTP password to avoid re-entering

## Email Body Templates

### Mid-Semester Message (Default)

The default email includes a disclaimer that these are progress grades:

```
Dear [Student Name],

Here is your individual grade report for [Course Name].

This report shows your current standing based on graded assignments 
completed so far this semester.

[Excel attachment details if available]

If you have any questions about your grades, please don't hesitate to reach out.

Best regards

────────────────────────
IMPORTANT DISCLAIMER:

This is just for the purpose of giving you an idea of how to compute 
your grade based on the work done so far. The percentage and letter 
grade is not a predictor of your final course grade, as it's missing 
a large part of the grade (final 35%, and several ungraded or 
unassigned psets, labs and quizlets). The computation of your current 
grade is done by normalizing the scores you have obtained with the 
maximum score possible in all the work graded so far.
────────────────────────
```

### Final Grades Message (--final-grades)

For end-of-semester final grades, use `--final-grades` flag:

```
Dear [Student Name],

Here is your final grade report for [Course Name].

This report shows your final course grade based on all graded 
assignments completed this semester.

[Excel attachment details if available]

These are your official final grades for the course. If you have any 
questions about your final grade calculation, please don't hesitate 
to reach out.

Thank you for your hard work this semester!

Best regards
```

To further customize the email body, edit the message templates in the `main()` function of `email_grades.py`.

## Troubleshooting

### Students with no email address
The script will skip students who don't have an email address in Canvas and report them in the summary.

### Students with no grade report
If a student's individual report file is missing from `individual-grades/`, they will be skipped.

### SMTP authentication errors
- For Gmail, you must use an "App Password" instead of your regular password
- Enable "Less secure app access" or use OAuth2 if your provider requires it
- Check that your SMTP credentials are correct

### Connection timeout
- Verify SMTP server hostname and port
- Check if TLS is required (most servers use TLS on port 587)
- Ensure your network allows outbound SMTP connections

### Relaying denied / IP name possibly forged
This error typically means:
- **MIT SMTP**: You must be on MIT network (use MIT VPN if off-campus), or the server requires Kerberos authentication
- **University SMTP**: Your IP address may not be authorized to relay mail through the server
- **Solution**: Use Gmail with an App Password, or contact your IT department for relay authorization

### Permission denied
The script may be blocked by institutional firewalls. Contact your IT department for SMTP relay access.

## Security Notes

- **Password Prompting (Recommended)**: Set `SMTP_PASSWORD` to `None` in CONFIG and the script will prompt you for the password at runtime
  - This is more secure as passwords aren't stored in files
  - Password input is hidden (no echo to screen)
- **Never commit passwords to version control** - Be careful if the script is in a git repository
- Consider using environment variables for sensitive credentials instead of hardcoding in CONFIG
- For Gmail, you **must** use App Passwords instead of your main password
  - Go to Google Account → Security → 2-Step Verification → App passwords
  - Generate a new app password for "Mail"
- Consider using a dedicated email account for automated sends
- Test thoroughly with `--test-email` before sending to students
- The CONFIG values are used as defaults but can be overridden by environment variables or command-line arguments

## Options Reference

```
--course-id ID              Canvas course ID (can be omitted if only one course)
--reports-dir DIR           Directory with grade reports (default: individual-grades)
--subject TEXT              Email subject line
--from-email ADDRESS        Sender email address
--smtp-server HOST          SMTP server hostname
--smtp-port PORT            SMTP server port
--smtp-user USER            SMTP username
--smtp-password PASS        SMTP password
--no-tls                    Disable TLS encryption
--test-config               Test email configuration and exit
--dry-run                   Show what would be sent without sending
--test-email ADDRESS        Send all emails to test address
--no-cache                  Download fresh data from Canvas
```
