

<beg_of_file_content>
# Canvas API Complete Guide

Comprehensive guide to using the Canvas API for course administration, configuration, and management.

## Table of Contents

1. [Overview](#overview)
2. [What You Can Do](#what-you-can-do)
3. [Permissions Required](#permissions-required)
4. [Course Management](#course-management)
5. [Assignment Groups](#assignment-groups)
6. [Assignments](#assignments)
7. [Grading](#grading)
8. [User Management](#user-management)
9. [Code Examples](#code-examples)
10. [Best Practices](#best-practices)

---

## Overview

The Canvas API provides programmatic access to almost all Canvas functionality. Using the `canvasapi` Python library, you can automate course setup, grading, and administration.

**Library:** `canvasapi` (https://canvasapi.readthedocs.io/)

**Installation:**
```bash
pip install canvasapi
```

---

## What You Can Do

### ✅ Available with Teacher/TA Privileges

| Task | Method | Notes |
|------|--------|-------|
| **Configure existing course** | `course.update()` | Change name, code, settings |
| **Course settings** | `course.update_settings()` | Hide grades, student features |
| **Create assignment groups** | `course.create_assignment_group()` | With weights and drop rules |
| **Edit assignment groups** | `assignment_group.edit()` | Change weights, drop rules |
| **Create assignments** | `course.create_assignment()` | Full configuration |
| **Edit assignments** | `assignment.edit()` | Due dates, points, etc. |
| **Get/set grades** | `submission.edit()` | Update student grades |
| **View roster** | `course.get_enrollments()` | See enrolled users |
| **View submissions** | `assignment.get_submissions()` | Access student work |

### ⚠️ Requires Admin Privileges

| Task | Method | Notes |
|------|--------|-------|
| **Create new course** | `account.create_course()` | Account admin only |
| **Enroll users** | `course.enroll_user()` | May require admin |
| **Create users** | `account.create_user()` | Account admin only |
| **Grading standards** | `course.create_grading_standard()` | May require admin |

---

## Permissions Required

### Your Current Access Level

Check your permissions:
```python
from canvas.connection import CanvasConnection

conn = CanvasConnection()
canvas = conn.get_canvas()
course = canvas.get_course(YOUR_COURSE_ID)

# Try to get course info
print(f"Course: {course.name}")
print(f"Can edit: {hasattr(course, 'update')}")
```

### Permission Levels

1. **Student**: Read-only access to own data
2. **TA**: Can grade, view submissions
3. **Teacher**: Full course management except creation
4. **Admin**: Can create courses, enroll users, modify accounts

---

## Course Management

### Get Existing Course

```python
from canvas.connection import CanvasConnection

conn = CanvasConnection()
canvas = conn.get_canvas()

# Get specific course
course = canvas.get_course(33045)
print(f"Course: {course.name}")
print(f"Code: {course.course_code}")
```

### Create New Course (Requires Admin)

```python
# Get account (typically ID 1 for root account)
account = canvas.get_account(1)

# Create course
course = account.create_course(
    course={
        "name": "16.001 Unified Engineering",
        "course_code": "16.001",
        "time_zone": "America/New_York",
    }
)
print(f"Created course ID: {course.id}")
```

### Update Course Settings

```python
# Update basic info
course.update(course={
    "name": "New Course Name",
    "course_code": "NEW.CODE",
    "apply_assignment_group_weights": True,
})

# Update course settings
course.update_settings(
    hide_final_grades=True,
    allow_student_discussion_topics=False,
)
```

### Get Course Settings

```python
settings = course.get_settings()
print(f"Hide final grades: {settings.get('hide_final_grades')}")
print(f"Weighted groups: {course.apply_assignment_group_weights}")
```

---

## Assignment Groups

### Create Assignment Groups with Weights

```python
# Enable weighted grading
course.update(course={"apply_assignment_group_weights": True})

# Create assignment group
problem_sets = course.create_assignment_group(
    name="Problem Sets",
    group_weight=15.0,  # 15% of final grade
    rules={
        "drop_lowest": 1,  # Drop lowest 1 assignment
    }
)

quizzes = course.create_assignment_group(
    name="Quizzes",
    group_weight=25.0,
    rules={
        "drop_lowest": 2,
    }
)

midterm = course.create_assignment_group(
    name="Midterm",
    group_weight=25.0,
    # No drop rules for midterm
)

final = course.create_assignment_group(
    name="Final Exam",
    group_weight=35.0,
)

print(f"Created 4 assignment groups, weights sum to 100%")
```

### Get Existing Assignment Groups

```python
groups = course.get_assignment_groups()
for group in groups:
    print(f"{group.name}:")
    print(f"  Weight: {group.group_weight}%")
    print(f"  ID: {group.id}")
    print(f"  Rules: {group.rules}")
```

### Edit Assignment Group

```python
# Get group
groups = course.get_assignment_groups()
ps_group = [g for g in groups if g.name == "Problem Sets"][0]

# Update weight and rules
ps_group.edit(
    group_weight=20.0,  # Change from 15% to 20%
    rules={"drop_lowest": 2}  # Change from 1 to 2
)
```

### Delete Assignment Group

```python
# Warning: This will delete all assignments in the group!
ps_group.delete()
```

---

## Assignments

### Create Assignment

```python
# Get assignment group ID
groups = course.get_assignment_groups()
ps_group = [g for g in groups if g.name == "Problem Sets"][0]

# Create assignment
assignment = course.create_assignment(
    assignment={
        "name": "Problem Set #1",
        "description": "Introduction to structural mechanics",
        "points_possible": 100,
        "grading_type": "points",  # or "percent", "letter_grade", etc.
        "submission_types": ["online_upload"],
        "assignment_group_id": ps_group.id,
        "due_at": "2025-09-15T23:59:00Z",  # ISO 8601 format
        "published": True,
    }
)

print(f"Created assignment ID: {assignment.id}")
```

### Assignment Options

```python
assignment = course.create_assignment(assignment={
    # Basic info
    "name": "Assignment Name",
    "description": "<p>HTML description</p>",
    "points_possible": 100,
    
    # Grading
    "grading_type": "points",  # points, percent, letter_grade, pass_fail
    "assignment_group_id": group.id,
    
    # Submission
    "submission_types": [
        "online_text_entry",
        "online_upload",
        "online_url",
        "on_paper",
        "none",
    ],
    "allowed_extensions": ["pdf", "docx"],  # If online_upload
    
    # Dates
    "due_at": "2025-12-15T23:59:00Z",
    "unlock_at": "2025-12-01T00:00:00Z",
    "lock_at": "2025-12-16T23:59:00Z",
    
    # Options
    "published": True,
    "omit_from_final_grade": False,
    "peer_reviews": False,
    "anonymous_grading": False,
    "grade_group_students_individually": False,  # For group assignments
})
```

### Edit Assignment

```python
assignment = course.get_assignment(12345)

assignment.edit(assignment={
    "points_possible": 120,  # Change points
    "due_at": "2025-09-20T23:59:00Z",  # Extend deadline
})
```

### Get All Assignments

```python
assignments = course.get_assignments()
for assignment in assignments:
    print(f"{assignment.name}:")
    print(f"  Points: {assignment.points_possible}")
    print(f"  Due: {assignment.due_at}")
    print(f"  Group: {assignment.assignment_group_id}")
```

---

## Grading

### Get Submissions

```python
assignment = course.get_assignment(12345)

# Get all submissions
submissions = assignment.get_submissions()
for sub in submissions:
    print(f"User {sub.user_id}: {sub.score}/{assignment.points_possible}")
    print(f"  Status: {sub.workflow_state}")  # submitted, graded, etc.
    print(f"  Submitted at: {sub.submitted_at}")
```

### Grade Submissions

```python
submission = assignment.get_submission(user_id=67890)

# Update grade
submission.edit(submission={
    "posted_grade": 85,  # or "B" for letter grades
    "comment": {
        "text_comment": "Good work! See comments on specific problems."
    }
})
```

### Bulk Grading

```python
# Grade multiple students
grades = {
    12345: 95,
    67890: 88,
    11111: 92,
}

for user_id, grade in grades.items():
    sub = assignment.get_submission(user_id)
    sub.edit(submission={"posted_grade": grade})
    print(f"Graded user {user_id}: {grade}")
```

### Grading Standards (Letter Grades)

```python
# Create grading standard
grading_standard = course.create_grading_standard(
    title="MIT Letter Grades",
    grading_scheme_entry=[
        {"name": "A", "value": 0.90},
        {"name": "B", "value": 0.80},
        {"name": "C", "value": 0.70},
        {"name": "D", "value": 0.60},
        {"name": "F", "value": 0.00},
    ]
)

# Apply to course
course.update(course={
    "grading_standard_id": grading_standard.id
})
```

---

## User Management

### Get Course Roster

```python
enrollments = course.get_enrollments()

students = []
for enrollment in enrollments:
    if enrollment.type == "StudentEnrollment":
        user = enrollment.user
        students.append({
            "id": user["id"],
            "name": user["name"],
            "email": user.get("email"),
        })

print(f"Found {len(students)} students")
```

### Enroll User (May Require Admin)

```python
# Enroll a student
enrollment = course.enroll_user(
    user=12345,  # User ID
    enrollment={
        "type": "StudentEnrollment",
        "enrollment_state": "active",
    }
)

# Enroll a TA
enrollment = course.enroll_user(
    user=67890,
    enrollment={
        "type": "TaEnrollment",
        "enrollment_state": "active",
    }
)
```

### Enrollment Types

- `StudentEnrollment` - Student
- `TeacherEnrollment` - Teacher/Instructor
- `TaEnrollment` - Teaching Assistant
- `ObserverEnrollment` - Observer (parent, mentor)
- `DesignerEnrollment` - Course Designer

---

## Code Examples

### Complete Course Setup

See `create_course_template.py` for a complete example that:
- Creates a course
- Sets up assignment groups with weights
- Creates sample assignments
- Configures grading standards

Run it:
```bash
# Dry-run to see what it would do
python3 create_course_template.py --dry-run

# Configure an existing course
python3 create_course_template.py --course-id 33045

# Create new course (requires admin)
python3 create_course_template.py --create-new --account-id 1
```

### Sync Assignment Groups to YAML

```python
from canvas.connection import CanvasConnection
import yaml

conn = CanvasConnection()
course = conn.get_canvas().get_course(33045)

# Get assignment groups
groups = course.get_assignment_groups()

# Build YAML config
config = {
    "use_canvas_groups": True,
    "drop_lowest": {}
}

for group in groups:
    rules = getattr(group, 'rules', {})
    if 'drop_lowest' in rules and rules['drop_lowest'] > 0:
        config['drop_lowest'][group.name] = rules['drop_lowest']

# Save to file
with open('grade_config.yaml', 'w') as f:
    yaml.dump(config, f)

print("Saved configuration from Canvas")
```

### Batch Create Assignments

```python
# List of assignments to create
assignments_data = [
    {"name": "Problem Set #1", "points": 100, "due": "2025-09-15"},
    {"name": "Problem Set #2", "points": 100, "due": "2025-09-22"},
    {"name": "Problem Set #3", "points": 100, "due": "2025-09-29"},
]

# Get assignment group
groups = course.get_assignment_groups()
ps_group = [g for g in groups if g.name == "Problem Sets"][0]

# Create all assignments
for data in assignments_data:
    assignment = course.create_assignment(assignment={
        "name": data["name"],
        "points_possible": data["points"],
        "due_at": f"{data['due']}T23:59:00Z",
        "assignment_group_id": ps_group.id,
        "published": True,
    })
    print(f"Created: {assignment.name}")
```

---

## Best Practices

### 1. Always Test with Dry-Run

```python
DRY_RUN = True  # Set to False when ready

if DRY_RUN:
    print("[DRY RUN] Would create assignment...")
else:
    assignment = course.create_assignment(...)
```

### 2. Error Handling

```python
try:
    course = canvas.get_course(course_id)
except canvasapi.exceptions.ResourceDoesNotExist:
    print(f"Course {course_id} not found")
except canvasapi.exceptions.Unauthorized:
    print("You don't have permission for this course")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### 3. Rate Limiting

Canvas has API rate limits. For bulk operations:

```python
import time

for i, data in enumerate(assignments_data):
    assignment = course.create_assignment(...)
    
    # Rate limit: max 1 request per second
    if i % 10 == 0:
        time.sleep(1)
```

### 4. Verify Before Modifying

```python
# Always check what you're modifying
assignment = course.get_assignment(12345)
print(f"About to modify: {assignment.name}")
print(f"Current points: {assignment.points_possible}")

# Confirm before proceeding
response = input("Continue? (y/n): ")
if response.lower() != 'y':
    print("Cancelled")
    exit()

assignment.edit(...)
```

### 5. Backup Configuration

```python
# Save current state before making changes
import json

groups = course.get_assignment_groups()
backup = [{
    "name": g.name,
    "weight": g.group_weight,
    "rules": g.rules,
} for g in groups]

with open(f'backup_course_{course.id}.json', 'w') as f:
    json.dump(backup, f, indent=2)

print("Backup saved")
```

### 6. Use Sandbox for Testing

Many Canvas instances have a "Sandbox" or "Test" environment:
- Test API calls there first
- Verify permissions and behavior
- Then apply to production courses

---

## Troubleshooting

### Common Errors

**"Unauthorized" / 403 Error:**
- Check your API token has correct permissions
- Some operations require teacher/admin role
- Verify you're enrolled in the course

**"Resource Does Not Exist" / 404 Error:**
- Course/assignment ID doesn't exist
- You don't have access to that resource
- Double-check IDs

**"Invalid Parameters" / 400 Error:**
- Check parameter names and formats
- Date formats must be ISO 8601: "2025-12-15T23:59:00Z"
- Some fields are required (name, points_possible, etc.)

**Rate Limit Exceeded / 429 Error:**
- Too many API requests
- Add delays between bulk operations
- Canvas typically allows 3000 requests/hour

---

## API Documentation

**Official Canvas API Docs:**
https://canvas.instructure.com/doc/api/

**Python canvasapi Library:**
https://canvasapi.readthedocs.io/

**Canvas API Token:**
- Settings → Approved Integrations → New Access Token
- Store securely in `canvas-token.json`

---

## See Also

- `create_course_template.py` - Complete course setup example
- `generate_config.py` - Generate config from Canvas
- `process_grades.py` - Read and process grades
- `CONFIGURATION_GUIDE.md` - Configuration options

---

## Summary

The Canvas API is powerful and comprehensive:

✅ **Full control** over course structure
✅ **Automate** repetitive tasks
✅ **Integrate** with external systems
✅ **Programmatic grading** and feedback
✅ **Bulk operations** for efficiency

⚠️ **Be careful**: Always test in sandbox first!
