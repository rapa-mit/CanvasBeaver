# Assignment Manager Guide

## Overview

`manage_assignments.py` is an interactive menu-driven script for managing Canvas assignments and grades. It provides a simple interface to:

1. **Add assignments** to specific assignment groups
2. **Upload grades** for assignments (via CSV or manual entry)
3. **List assignment groups** and assignments

## Features

- **Reuses existing connection infrastructure** from `process_grades.py` and `create_course_template.py`
- **Interactive menu system** for easy navigation
- **Multiple grade upload methods**: CSV file or manual entry
- **Safe and validated**: Confirms actions before making changes
- **Course selection**: Automatically prompts for course if not specified

## Usage

### Basic Usage

```bash
# Interactive course selection
python3 manage_assignments.py

# Specify course ID directly
python3 manage_assignments.py --course-id 12345
```

### Menu Options

Once launched, you'll see a menu with these options:

```
1. Add assignment to assignment group
2. Upload grades for an assignment
3. List assignment groups
4. List assignments
5. Publish/unpublish an assignment
6. Test grade upload permissions
0. Exit
```

## Adding an Assignment

**Note**: Creating assignments typically requires Teacher enrollment (admins may not have this permission by default).

When you select **Option 1: Add assignment to assignment group**, the script will:

1. Display all available assignment groups
2. Prompt you to select a group
3. Ask for assignment details:
   - Assignment name
   - Points possible
   - Due date (optional)
   - Description (optional)
   - Submission type (upload, text entry, URL, or none)
4. Show a summary and ask for confirmation
5. Create the assignment in Canvas

### Example

```
Select option: 1

Available assignment groups:
  1. Problem Sets (15.0%)
  2. Quizlets (25.0%)
  3. Midterm (25.0%)
  4. Final Exam (35.0%)

Select assignment group (number): 1

Selected group: Problem Sets

Assignment name: Problem Set #5
Points possible: 100
Due date (YYYY-MM-DD HH:MM or leave blank): 2025-12-20 23:59
Description (optional): Covers chapters 10-12

Submission types:
  1. online_upload (file upload)
  2. online_text_entry (text entry)
  3. online_url (URL)
  4. none (no submission)
Select submission type (1-4): 1

Publish assignment?
  Note: Unpublished assignments typically cannot receive grades
Publish now? (Y/n): y

Assignment details:
  Name: Problem Set #5
  Group: Problem Sets
  Points: 100.0
  Due: 2025-12-20 23:59
  Submission type: online_upload
  Published: Yes

Create this assignment? (y/n): y

Creating assignment...
✅ Assignment created successfully!
   ID: 98765
   Name: Problem Set #5
   Status: Published
```

## Uploading Grades

When you select **Option 2: Upload grades for an assignment**, you can choose between two methods:

### Method 1: CSV File Upload

Create a CSV file with the following format:

```csv
Name,MIT ID,Percent Attendance
Alice Johnson,123456789,95
Bob Smith,987654321,88.5
Charlie Davis,456789123,92
```

**CSV Requirements:**
- Must have a student identifier column (MIT ID, student_id, or Canvas user ID)
- Must have a grade/score column (detected automatically or uses last column)
- Optionally include a Name column for readability

**Flexible Column Detection:**
- The script automatically detects column names (case-insensitive)
- ID columns: "MIT ID", "student_id", "id", "canvas_id", "user_id"
- Grade columns: "grade", "score", "points", "percent", "attendance" (or last column)
- Name columns: "name", "student", "student name" (optional, for display only)

The script will:
1. Read the CSV file
2. Show a preview of grades to upload
3. Ask for confirmation
4. Upload each grade to Canvas
5. Show success/error count

### Method 2: Manual Entry

The script will:
1. Fetch all active students in the course
2. Prompt you to enter a grade for each student
3. Allow skipping students (press Enter)
4. Show summary and ask for confirmation
5. Upload the grades to Canvas

### Example (CSV Method)

```
Select option: 2

Available assignments:
  1. Problem Set #1 (100.0 points, ID: 11111)
  2. Problem Set #2 (100.0 points, ID: 22222)
  3. Quizlet #1 (10.0 points, ID: 33333)

Select assignment (number) or enter assignment ID: 1

Selected assignment: Problem Set #1
Points possible: 100.0

Grade input methods:
  1. CSV file (columns: student_id, grade)
  2. Manual entry (interactive)

Select method (1-2): 1

Enter CSV file path: grades_ps1.csv

Reading CSV file...

Detecting CSV format...
Found columns: Name, MIT ID, Percent Attendance
Using ID column: 'MIT ID'
Using grade column: 'Percent Attendance'
Using name column: 'Name'

Building student lookup table...
Found 25 students with MIT IDs

Found 25 grades to upload.
Preview:
  Alice Johnson: 95
  Bob Smith: 88.5
  Charlie Davis: 92
  Diana Martinez: 78
  Eve Wilson: 100
  ... and 20 more

Upload these grades? (y/n): y

Uploading grades...
  ✅ Alice Johnson: 95
  ✅ Bob Smith: 88.5
  ✅ Charlie Davis: 92
  ...

✅ Upload complete!
   Successful: 25
   Errors: 0
```

## Integration with Existing Scripts

The script reuses infrastructure from:

- **`canvas/connection.py`**: Canvas API connection management
- **`canvas/course.py`**: Course selection and operations
- **`process_grades.py`**: Pattern for Canvas API usage

This ensures consistency and maintainability across your Canvas management tools.

## CSV Format Examples

The script supports flexible CSV formats. Here are some valid examples:

**Example 1: Name, MIT ID, Grade**
```csv
Name,MIT ID,Percent Attendance
Alice Johnson,123456789,95
Bob Smith,987654321,88.5
```

**Example 2: Simple format**
```csv
student_id,grade
123456789,95
987654321,88.5
```

**Example 3: Canvas user IDs**
```csv
canvas_id,score
12345,95
67890,88.5
```

The script will automatically:
- Detect which column contains student IDs (MIT ID preferred)
- Detect which column contains grades/scores
- Look up Canvas user IDs from MIT IDs
- Display student names in the preview if available

## Publishing Assignments

Use menu option 5 to publish or unpublish assignments:

```
Select option: 5

Available assignments:
  1. Problem Set #1 (100 pts) - ✓ Published
  2. Problem Set #2 (100 pts) - ✗ Unpublished
  3. Quizlet #1 (10 pts) - ✓ Published

Select assignment (number) or enter assignment ID: 2

Selected: Problem Set #2
Current status: Unpublished

Publish this assignment? (Y/n): y

Publishing assignment...
✅ Assignment published successfully!
   Students can now see this assignment and submit work.
   You can now upload grades for this assignment.
```

**Important**: Unpublished assignments typically **cannot receive grades**. Always publish assignments before uploading grades.

## Tips

1. **Publish before grading**: Always publish assignments before attempting to upload grades
2. **Test with one grade first**: When using CSV upload, test with a small file first
3. **Check assignment groups**: Use option 3 to verify groups before creating assignments
4. **Verify assignment ID**: Use option 4 to list assignments and confirm IDs (✓ = published, ✗ = unpublished)
5. **Keep CSV backups**: Save your grade CSV files as backups before uploading
6. **Use descriptive names**: Give assignments clear names to avoid confusion
7. **MIT ID vs Canvas ID**: The script prefers MIT IDs (sis_user_id) but also accepts Canvas user IDs

## Error Handling

The script includes error handling for common issues:
- Invalid file paths
- Missing CSV columns
- Invalid student IDs
- Canvas API errors
- Network issues
- Permission errors

Errors are displayed with ❌ and descriptive messages.

## Troubleshooting

### "Permission Error: You need Teacher or TA enrollment"

**Problem**: You're trying to upload grades but don't have the right enrollment type.

**Solution**:
1. Contact your course administrator
2. Ask them to enroll you as a **Teacher** or **TA** (not just give admin access)
3. They can do this in Canvas under: Course Settings → People → Add People

### Cannot Upload Grades to Assignment

**Problem**: You get permission errors when trying to upload grades.

**Most Common Cause**: The assignment is **unpublished** (in draft mode).

**Solution**: Publish the assignment first:
1. Use menu option 5 "Publish/unpublish an assignment"
2. Or when creating assignments, answer "Y" to "Publish now?"
3. Or publish manually in Canvas

**Other Possible Causes**:
- Assignment has muted/anonymous grading enabled
- Assignment is locked or has special grading rules
- Canvas API token has limited scope (rare - see `TOKEN_TROUBLESHOOTING.md`)

**Quick Test**: Use menu option 6 "Test grade upload permissions" to diagnose the issue.

### "Could not find student with ID..."

**Problem**: A student ID in your CSV doesn't match any enrolled student.

**Solutions**:
- Verify the MIT ID is correct (9 digits)
- Check if the student is enrolled in the course
- Ensure the student's MIT ID is set in Canvas (sis_user_id field)
- Try using Canvas user IDs instead of MIT IDs

### "CSV must have student_id and grade columns"

**Problem**: The script couldn't auto-detect your CSV format.

**Solution**:
- Make sure your CSV has clear column headers
- Use recognizable names like "MIT ID", "student_id", "grade", "score", etc.
- See the CSV Format Examples section for valid formats

## Requirements

- Python 3.7+
- canvasapi library (from requirements.txt)
- Valid Canvas API token in `canvas-token.json`
- **Teacher or TA enrollment** in the course (required for uploading grades)

### Important: Permission Requirements

**To upload grades**, you must be enrolled in the course with one of these roles:
- **Teacher** (full permissions)
- **TA** (Teaching Assistant - can grade)

**Admin access alone is NOT sufficient** to upload grades. If you have admin access but cannot upload grades:

1. Have a course administrator add you as a Teacher or TA to the course
2. Or, ask someone with Teacher enrollment to use the script
3. Alternatively, use Canvas's built-in grade import feature

The script will check your permissions before attempting to upload grades and provide helpful error messages if you lack the necessary enrollment.

## Security Notes

- Your Canvas API token is stored in `canvas-token.json` (not in the script)
- The script only modifies the course you specify
- All changes require confirmation before execution
- Grade uploads show previews before applying changes
