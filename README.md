# Canvas Grade Processor & Email System

A comprehensive Python toolkit for processing Canvas gradebook data with advanced features for grade computation, Excel report generation, and automated email distribution to students.

## Overview

This toolkit provides a complete grade management system:
- Download gradebook data directly from Canvas via API
- Process grades with configurable weights and drop-lowest policies
- Generate individual student reports (text and Excel with formulas)
- Email grade reports to students with password caching
- Detect anomalies and grade patterns
- Export results in various formats

## Quick Start

### 1. Set Up Canvas API Access
Create `canvas.json` with your Canvas credentials or export your API token:
```bash
export CANVAS_TOKEN="<your token here>"
```

### 2. Process Grades
```bash
python3 process_grades.py --config grade_config_canvas.yaml
```

This generates:
- Individual text reports (`individual-grades/*.txt`)
- Individual Excel spreadsheets with formulas (`individual-grades/*.xlsx`)
- Summary CSV (`grades_summary.csv`)

### 3. Email Grades to Students
```bash
# Test first (doesn't actually send)
./email_grades.py --course-id XXXXX --dry-run

# Send to yourself to verify
./email_grades.py --course-id XXXXX --test-email your@email.com

# Send to all students
./email_grades.py --course-id XXXXX
```

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
- **[README.md](README.md)** - This file - overview and reference

### Grade Processing
- **[GRADE_PROCESSING.md](GRADE_PROCESSING.md)** - Complete grade processing documentation including:
  - Canvas API integration details
  - Configuration options and examples
  - Weight calculation methods
  - Drop-lowest implementation
  - Anomaly detection algorithms
  - Output formats
  
- **[PARTIAL_GRADING_GUIDE.md](PARTIAL_GRADING_GUIDE.md)** - Mid-semester grading guide covering:
  - Handling incomplete assignment sets
  - Weight normalization for partial semesters
  - Configuration for graded-only assignments
  - Interpreting normalized grades
  
- **[DROP_LOWEST_UPDATE.md](DROP_LOWEST_UPDATE.md)** - Drop-lowest feature documentation:
  - How drop-lowest works by category
  - Configuration examples
  - Edge cases and limitations
  - Impact on grade calculations
  
- **[SIMPLIFIED_CALCULATION.md](SIMPLIFIED_CALCULATION.md)** - Grade calculation overview:
  - Step-by-step calculation walkthrough
  - Examples with real numbers
  - Formula explanations
  - Troubleshooting common issues

### Email System
- **[EMAIL_SETUP.md](EMAIL_SETUP.md)** - Complete email configuration and usage guide including:
  - SMTP configuration (Gmail, MIT, custom servers)
  - Password caching and security
  - Email body customization
  - Testing and dry-run modes
  - Troubleshooting common email issues
  - Excel attachment handling

### Technical Details
- **[CACHING_FEATURE.md](CACHING_FEATURE.md)** - Gradebook caching system:
  - Cache file format and location
  - Cache invalidation strategies
  - Performance benefits
  - Manual cache management
  
- **[REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md)** - Code architecture and design decisions:
  - Module structure
  - API design patterns
  - Refactoring history
  - Extension points
  
- **[FINAL_SUMMARY.md](FINAL_SUMMARY.md)** - System overview and feature summary:
  - Complete feature list
  - System architecture
  - Data flow
  - Integration points

## Configuration Files

### Grade Configuration
- `grade_config_canvas.yaml` - Production grade configuration
- `grade_config_example.yaml` - Template for custom configurations

### Letter Grade Scales
- `MIT-letter-grades.yaml` - MIT 5.0 scale (default)
- `strict-letter-grades.yaml` - Traditional 4.0 scale

## Main Scripts

### Core Processing
- `process_grades.py` - Main grade processing script
- `email_grades.py` - Email distribution script

### Utilities
- `list_courses.py` - List available Canvas courses
- `list_assignments.py` - Show assignments for a course
- `print_roster.py` - Display course roster
- `analyze_grades.py` - Grade analysis tools
- `diagnose_assignments.py` - Assignment debugging

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

- Never commit `canvas.json` (contains API credentials)
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

# 3. Preview what will be sent (dry run)
./email_grades.py --course-id 33045 --dry-run

# 4. Send to yourself first
./email_grades.py --course-id 33045 --test-email your@email.com

# 5. Send to all students
./email_grades.py --course-id 33045
```

## License

This toolkit is for educational use. Adapt as needed for your institution.
