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

**Requirements:**
- Python 3.7 or higher
- Works on Windows, macOS, and Linux

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

### 2. Configuration Setup

You have several options for configuration:

#### Option A: Auto-Config (No YAML needed!)
```bash
# Simplest - auto-detect everything from Canvas
python3 process_grades.py --auto-config

# Auto-detect with Canvas drop rules (if configured in Canvas)
python3 process_grades.py --auto-config --course-id XXXXX
```

#### Option B: Generate Config File
```bash
# Generate config file from Canvas (then edit drop_lowest as needed)
python3 generate_config.py --interactive

# Or use shortcut from process_grades
python3 process_grades.py --generate-config
```

#### Option C: Use Existing Config File
```bash
# Use pre-configured YAML file
python3 process_grades.py --config grade_config_canvas.yaml
```

### 3. Process Grades

```bash
# Basic usage with config file
python3 process_grades.py --config grade_config_canvas.yaml

# Or use auto-config (no YAML needed)
python3 process_grades.py --auto-config

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
- `--config FILE` - Configuration YAML file (optional with --auto-config)
- `--auto-config` - Auto-detect configuration from Canvas (no YAML needed)
- `--generate-config` - Generate config file and exit
- `--course-id ID` - Canvas course ID (interactive if not specified)
- `--include-ungraded` - Include ungraded assignments (default: only graded)
- `--include-inactive` - Include inactive student enrollments
- `--output-dir DIR` - Output directory (default: `{course}-{date}`)
- `--no-cache` - Skip cache, download fresh from Canvas
- `--modified-grade-scale FILE` - Use alternative letter grade scale (see [MODIFIED_GRADE_SCALE.md](MODIFIED_GRADE_SCALE.md))

**Generates:**
- Individual text reports (`{course}-{date}/individual-grades/*.txt`)
- Individual Excel spreadsheets with formulas (`{course}-{date}/individual-grades/*.xlsx`)
- Summary CSV (`{course}-{date}/grades_summary.csv`)
- Anomaly report (`{course}-{date}/anomaly_report.txt`)

### 4. Email Grades to Students
```bash
# Test email configuration first
python3 email_grades.py --test-config

# Preview what will be sent (dry run)
python3 email_grades.py --dry-run

# Send to yourself to verify
python3 email_grades.py --test-email your@email.com

# Send to all students (mid-semester) - asks for confirmation before each email
python3 email_grades.py

# Send final grades (end of semester)
python3 email_grades.py --final-grades

# Send without individual confirmations (batch mode)
python3 email_grades.py --final-grades --no-confirm

# Specify course ID explicitly
python3 email_grades.py --course-id XXXXX --final-grades

# Use custom reports directory
python3 email_grades.py --reports-dir ./custom-reports/individual-grades
```

**Note:** The script will prompt you for:
- Course selection (if not specified with `--course-id`)
- SMTP password (cached securely after first use)
- Confirmation before sending

By default, `email_grades.py` automatically looks for reports in `{course}-{date}/individual-grades`.

## Configuration Modes

### Auto-Config Mode (Recommended)
Use `--auto-config` for zero-configuration setup:
- Automatically fetches assignment groups and weights from Canvas
- Auto-detects drop rules if configured in Canvas
- No YAML file needed
- Perfect for simple use cases

### Generated Config Mode
Use `generate_config.py` or `--generate-config`:
- Scans Canvas and creates a YAML template
- Optionally prompts for drop_lowest values (--interactive)
- Edit the generated file to customize
- Provides full control over drop rules

### Manual Config Mode
Create your own YAML file:
- Full control over all settings
- Can override Canvas weights
- Useful for complex grading scenarios
- See `grade_config_example.yaml` for template

## Key Features

### Grade Processing
- **Direct Canvas API integration** - No CSV exports needed
- **Auto-configuration** - Works with or without YAML files
- **Configurable grade weights** - Pulled from Canvas or manual
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

- **[CONFIGURATION_GUIDE.md](CONFIGURATION_GUIDE.md)** - **Configuration guide** (recommended):
  - Three configuration modes (auto, generate, manual)
  - Canvas drop rules support
  - Letter grade scales
  - Troubleshooting and best practices
  - Complete examples

- **[CANVAS_API_GUIDE.md](CANVAS_API_GUIDE.md)** - **Canvas API programming guide**:
  - Create and configure courses programmatically
  - Set up assignment groups with weights and drop rules
  - Create assignments and manage grading
  - Enroll users and manage roster
  - Complete code examples and best practices

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

- **[MODIFIED_GRADE_SCALE.md](MODIFIED_GRADE_SCALE.md)** - Modified letter grade scales:
  - Using alternative grading scales
  - Comparing different grading policies
  - Side-by-side grade display in all reports
  - Weight normalization explained with examples
  - Configuration for graded-only assignments
  - Interpreting normalized vs. raw grades
  - When to use partial grading mode
  
- **[EMAIL_SETUP.md](EMAIL_SETUP.md)** - Email distribution system:
  - SMTP configuration for different providers (Gmail, MIT, custom)
  - Password caching with secure storage
  - Interactive confirmation mode (ask before each email)
  - Batch mode with `--no-confirm` flag
  - Email body format and customization
  - Excel attachment handling
  - Testing modes (dry-run, test-email)
  - Troubleshooting common issues
  - Security best practices

- **[EMAIL_INTERACTIVE_GUIDE.md](EMAIL_INTERACTIVE_GUIDE.md)** - Interactive email confirmation:
  - How interactive confirmation works
  - Available options (yes/no/quit/preview/all)
  - Example workflows and use cases
  - When to use batch mode vs interactive mode

- **[FINAL_GRADES_MESSAGE.md](FINAL_GRADES_MESSAGE.md)** - Final grades email message:
  - Using `--final-grades` flag for end-of-semester
  - Comparison of mid-semester vs final messages
  - When to use each message type
  - Complete workflow examples

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
- `CONFIGURATION_GUIDE.md` - **Complete configuration guide** (recommended reading)

### Letter Grade Scales
- `MIT-letter-grades.yaml` - MIT 5.0 scale (default)
- `strict-letter-grades.yaml` - Traditional 4.0 scale

## Main Scripts

### Core Processing

**`generate_config.py`** - Generate configuration from Canvas
```bash
# Interactive mode - prompts for drop_lowest values
python3 generate_config.py --interactive

# Non-interactive - creates template to edit
python3 generate_config.py --course-id 33045

Options:
  --course-id ID          Canvas course ID (interactive if omitted)
  --output FILE           Output YAML file
  --interactive           Prompt for drop_lowest values
  --force                 Overwrite existing config file
```

**`process_grades.py`** - Main grade processing script
```bash
# With auto-config (no YAML needed)
python3 process_grades.py --auto-config

# With config file
python3 process_grades.py --config grade_config_canvas.yaml [OPTIONS]

Options:
  --config FILE           Configuration YAML file (optional with --auto-config)
  --auto-config           Auto-detect config from Canvas (no YAML needed)
  --generate-config       Generate config file and exit
  --course-id ID          Canvas course ID (interactive if omitted)
  --include-ungraded      Include all assignments, even ungraded
  --include-inactive      Include inactive student enrollments
  --output-dir DIR        Output directory (default: {course}-{date})
  --no-cache              Skip cache, download fresh from Canvas
```

**`create_course_template.py`** - Canvas API course builder
```bash
# Show what it would do (safe dry-run)
python3 create_course_template.py --dry-run

# Configure existing course
python3 create_course_template.py --course-id 33045

# Setup assignment groups only
python3 create_course_template.py --course-id 33045 --setup-groups-only

# Create new course (requires admin)
python3 create_course_template.py --create-new --account-id 1

Options:
  --course-id ID          Existing course to configure
  --create-new            Create new course (requires admin)
  --account-id ID         Account ID for new course (default: 1)
  --dry-run               Show what would be done without changes
  --setup-groups-only     Only setup assignment groups
```

**`email_grades.py`** - Email distribution script
```bash
python3 email_grades.py [OPTIONS]

Options:
  --test-config           Test SMTP configuration
  --dry-run               Show what would be sent without sending
  --test-email EMAIL      Send all emails to this address instead
  --course-id ID          Canvas course ID (interactive if omitted)
  --reports-dir DIR       Directory with grade reports (default: {course}-{date}/individual-grades)
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
