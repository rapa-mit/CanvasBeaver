# Canvas Beaver

**Building Better Grade Reports**

A comprehensive Python toolkit for processing Canvas gradebook data with advanced features for grade computation, Excel report generation, and automated email distribution to students.

## Overview

This toolkit provides a complete grade management system:
- Download gradebook data directly from Canvas via API
- Process grades with configurable weights and drop-lowest policies
- Generate individual student reports (text and Excel with formulas)
- Email grade reports to students with password caching
- Detect anomalies and grade patterns
- Export results in various formats

## Installation

```bash
# Clone the repository
git clone git@github.com:rapa-mit/CanvasBeaver.git
cd CanvasBeaver

# Install dependencies
pip install canvasapi openpyxl pyyaml
```

## Quick Start

### 1. Set Up Canvas API Access

#### Obtaining Your Canvas API Token

To use this toolkit, you need a Canvas API access token. Here's how to get one:

1. **Log in to Canvas** at your institution's Canvas URL (e.g., `https://canvas.mit.edu`)

2. **Navigate to Account Settings**:
   - Click on "Account" in the left navigation menu
   - Select "Settings" from the dropdown

3. **Generate a New Access Token**:
   - Scroll down to the "Approved Integrations" section
   - Click the "+ New Access Token" button
   - Give your token a purpose/name (e.g., "Grade Processing Tool")
   - (Optional) Set an expiration date for security
   - Click "Generate Token"

4. **Copy Your Token**:
   - Canvas will display your token **only once**
   - Copy it immediately and store it securely
   - ⚠️ **Important:** You won't be able to see this token again. If you lose it, you'll need to generate a new one.

5. **Configure the Token**:
   
   The toolkit will automatically prompt you for your token the first time you run any command. It will then save it to `canvas-token.json` for future use.
   
   Alternatively, you can create `canvas-token.json` manually:
   ```json
   {
     "api_url": "https://canvas.mit.edu",
     "api_key": "your_token_here"
   }
   ```
   ⚠️ **Security:** Never commit `canvas-token.json` to version control!

**Note:** The token provides access to your Canvas account data. Keep it secure and never share it publicly.

### 2. Process Grades
```bash
# Basic usage (recommended for mid-semester)
python3 process_grades.py --config grade_config_canvas.yaml

# Specify course ID explicitly
python3 process_grades.py --config grade_config_canvas.yaml --course-id XXXXX

# End of semester (include all assignments, even ungraded)
python3 process_grades.py --config grade_config_canvas.yaml --include-ungraded

# Custom output directory
python3 process_grades.py --config grade_config_canvas.yaml --output-dir ./reports

# Force fresh download (skip cache)
python3 process_grades.py --config grade_config_canvas.yaml --no-cache
```

**Options:**
- `--config FILE` - Configuration YAML file (required)
- `--course-id ID` - Canvas course ID (interactive if not specified)
- `--include-ungraded` - Include ungraded assignments (default: only graded)
- `--include-inactive` - Include inactive student enrollments
- `--output-dir DIR` - Output directory (default: current directory)
- `--no-cache` - Skip cache, download fresh from Canvas

**Generates:**
- Individual text reports (`individual-grades/*.txt`)
- Individual Excel spreadsheets with formulas (`individual-grades/*.xlsx`)
- Summary CSV (`grades_summary.csv`)
- Anomaly report (`anomaly_report.txt`)

### 3. Email Grades to Students
```bash
# Test email configuration first
./email_grades.py --test-config

# Preview what will be sent (dry run)
./email_grades.py --dry-run

# Send to yourself to verify
./email_grades.py --test-email your@email.com

# Send to all students
./email_grades.py

# Specify course ID explicitly
./email_grades.py --course-id XXXXX
```

**Note:** The script will prompt you for:
- Course selection (if not specified with `--course-id`)
- SMTP password (cached securely after first use)
- Confirmation before sending

## Key Features

### Grade Processing
- **Direct Canvas API integration** - No CSV exports needed
- **Configurable grade weights** - Flexible category weighting
- **Drop lowest grades** - By category (e.g., drop 1 quiz)
- **Partial semester grading** - Handles mid-semester with normalization
- **Letter grade computation** - Configurable grade scales
- **Anomaly detection** - Identify unusual grade patterns
- **Caching** - Efficient gradebook caching to avoid repeated API calls

### Excel Reports
- **Interactive spreadsheets** - Each student gets an Excel file
- **Live formulas** - Shows exactly how grades are calculated
- **Category breakdowns** - Assignments organized by type
- **Grade conversion table** - Separate sheet with letter grade scale
- **What-if analysis** - Students can modify hypothetical scores
- **Professional formatting** - Color-coded, bordered cells

### Email Distribution
- **Automatic email retrieval** - Gets student emails from Canvas
- **Inlined text reports** - Full report in email body
- **Excel attachments** - Interactive spreadsheet attached
- **Password caching** - Secure password storage with retry on failure
- **SMTP configuration** - Supports Gmail, MIT, and custom SMTP
- **Safe testing modes** - Dry-run and test-email options

## Documentation

### Getting Started
- **[QUICK_START.txt](QUICK_START.txt)** - Quick start guide with step-by-step instructions for first-time setup and basic usage

### Core Documentation

- **[GRADE_PROCESSING.md](GRADE_PROCESSING.md)** - Complete grade processing documentation:
  - Canvas API integration and configuration
  - Weight calculation methods (Canvas groups vs. manual)
  - Drop-lowest grades by category with examples
  - Anomaly detection algorithms and interpretation
  - Configuration file format and options
  - Output formats (CSV, text, Excel)
  - Command-line usage and examples
  
- **[PARTIAL_GRADING_GUIDE.md](PARTIAL_GRADING_GUIDE.md)** - Mid-semester grading:
  - How partial semester grading works
  - Weight normalization explained with examples
  - Configuration for graded-only assignments
  - Interpreting normalized vs. raw grades
  - When to use partial grading mode
  
- **[EMAIL_SETUP.md](EMAIL_SETUP.md)** - Email distribution system:
  - SMTP configuration for different providers (Gmail, MIT, custom)
  - Password caching with secure storage
  - Email body format and customization
  - Excel attachment handling
  - Testing modes (dry-run, test-email)
  - Troubleshooting common issues
  - Security best practices

### Technical Documentation
- **[CACHING_FEATURE.md](CACHING_FEATURE.md)** - Gradebook caching:
  - How caching works and performance benefits
  - Cache file format (.pkl) and location
  - Cache invalidation and refresh strategies
  - Manual cache management commands
  - When to use `--no-cache` option

## Configuration Files

### Grade Configuration
- `grade_config_canvas.yaml` - Production grade configuration
- `grade_config_example.yaml` - Template for custom configurations

### Letter Grade Scales
- `MIT-letter-grades.yaml` - MIT 5.0 scale (default)
- `strict-letter-grades.yaml` - Traditional 4.0 scale

## Main Scripts

### Core Processing

**`process_grades.py`** - Main grade processing script
```bash
python3 process_grades.py --config grade_config_canvas.yaml [OPTIONS]

Options:
  --config FILE           Configuration YAML file (required)
  --course-id ID          Canvas course ID (interactive if omitted)
  --include-ungraded      Include all assignments, even ungraded
  --include-inactive      Include inactive student enrollments
  --output-dir DIR        Output directory (default: current directory)
  --no-cache              Skip cache, download fresh from Canvas
```

**`email_grades.py`** - Email distribution script
```bash
./email_grades.py [OPTIONS]

Options:
  --test-config           Test SMTP configuration
  --dry-run               Show what would be sent without sending
  --test-email EMAIL      Send all emails to this address instead
  --course-id ID          Canvas course ID (interactive if omitted)
  --reports-dir DIR       Directory with grade reports (default: individual-grades)
  --subject SUBJECT       Email subject line
  --from-email EMAIL      Sender email address
  --smtp-server HOST      SMTP server hostname
  --smtp-port PORT        SMTP port (default: 465)
  --smtp-user USER        SMTP username
  --smtp-password PASS    SMTP password
  --no-tls                Disable TLS encryption
  --no-cache              Skip cache, download fresh from Canvas
```

### Utilities

**`list_courses.py`** - List available Canvas courses
```bash
python3 list_courses.py
```
Shows all active courses with IDs and enrollment info.

**`list_assignments.py`** - Show assignments for a course
```bash
python3 list_assignments.py [--course-id ID]
```
Lists all assignments with groups, points, and due dates.

**`print_roster.py`** - Display course roster
```bash
python3 print_roster.py [--course-id ID] [--include-inactive]

Options:
  --course-id ID          Canvas course ID (interactive if omitted)
  --include-inactive      Include inactive enrollments
```

**`analyze_grades.py`** - Grade analysis tools
```bash
python3 analyze_grades.py [--course-id ID] [--student-id ID] [--include-inactive]

Options:
  --course-id ID          Canvas course ID (interactive if omitted)
  --student-id ID         Show details for specific student
  --include-inactive      Include inactive enrollments
```

**`diagnose_assignments.py`** - Assignment debugging
```bash
python3 diagnose_assignments.py
```
Helps diagnose assignment detection and grading issues.

### Testing

- `test_grades.py` - Grade computation tests
- `test_drop_lowest.py` - Drop-lowest feature tests
- `test_partial_grading.py` - Partial semester tests
- `test_roster.py` - Roster tests

## Canvas Module

The `canvas/` directory contains the core library:
- `connection.py` - Canvas API connection management
- `gradebook.py` - Gradebook data structures and caching
- `grade_processor.py` - Grade computation and Excel generation
- `course.py` - Course management
- `course_selector.py` - Interactive course selection
- `assignment.py` - Assignment handling
- `roster.py` - Student roster management

## Requirements

- Python 3.8+
- canvasapi library
- openpyxl library (for Excel generation)
- pyyaml library
- smtplib (standard library, for email)

## Security Notes

- Never commit `canvas-token.json` (contains API credentials)
- Never commit `.canvas_session.json` (contains session data)
- Password caching uses secure file permissions (0600)
- Use environment variables for sensitive SMTP credentials
- For Gmail, use App Passwords, not your main password

## Workflow Example

```bash
# 1. Process grades and generate reports
python3 process_grades.py --config grade_config_canvas.yaml

# 2. Test email configuration
./email_grades.py --test-config

# 3. Preview what will be sent (dry run - no course ID needed)
./email_grades.py --dry-run

# 4. Send to yourself first
./email_grades.py --test-email your@email.com

# 5. Send to all students
./email_grades.py
```

**Note:** Course selection is interactive if `--course-id` is not specified.

## License

This toolkit is for educational use. Adapt as needed for your institution.
