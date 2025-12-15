#!/usr/bin/env python3
"""
manage_assignments.py
--------------------------------
Interactive menu-driven script for managing Canvas assignments.

Features:
- Add assignments to specific assignment groups
- Upload grades for assignments
- Reuses connection infrastructure from existing scripts

Usage:
  python3 manage_assignments.py [--course-id ID]
  
  If course-id is not provided, you'll be prompted to select a course.
"""
from __future__ import annotations

import argparse
import sys
from typing import Optional, Dict, Any, List
import csv
from pathlib import Path

from canvas.connection import CanvasConnection
from canvas.course import Course


class AssignmentManager:
    """Manage Canvas assignments and grades."""
    
    def __init__(self, canvas_connection: CanvasConnection, course: Course):
        self.conn = canvas_connection
        self.course = course
        self.canvas = canvas_connection.get_canvas()
        self.canvas_course = course.canvas_course
    
    def show_menu(self):
        """Display the main menu and handle user selection."""
        while True:
            print("\n" + "=" * 70)
            print("CANVAS ASSIGNMENT MANAGER")
            print("=" * 70)
            print(f"Course: {self.course.name} (ID: {self.course.course_id})")
            print("\nOptions:")
            print("  1. Add assignment to assignment group")
            print("  2. Upload grades for an assignment")
            print("  3. List assignment groups")
            print("  4. List assignments")
            print("  5. Publish/unpublish an assignment")
            print("  6. Test grade upload permissions")
            print("  0. Exit")
            print("=" * 70)
            
            choice = input("\nSelect option: ").strip()
            
            if choice == "1":
                self.add_assignment()
            elif choice == "2":
                self.upload_grades()
            elif choice == "3":
                self.list_assignment_groups()
            elif choice == "4":
                self.list_assignments()
            elif choice == "5":
                self.publish_assignment()
            elif choice == "6":
                self.test_permissions()
            elif choice == "0":
                print("\nExiting...")
                break
            else:
                print("\n❌ Invalid option. Please try again.")
    
    def test_permissions(self):
        """Test if we can upload grades by attempting a read-only check."""
        print("\n" + "=" * 70)
        print("PERMISSION TEST")
        print("=" * 70)
        
        print("\n1. Checking your enrollment...")
        try:
            # Check enrollment type
            enrollments = list(self.canvas_course.get_enrollments(user_id='self'))
            
            if enrollments:
                for e in enrollments:
                    role = e.type
                    state = getattr(e, 'enrollment_state', 'unknown')
                    print(f"   ✓ Enrollment: {role} ({state})")
            else:
                print("   ⚠ No enrollment found for you in this course")
        except Exception as e:
            print(f"   ❌ Error checking enrollment: {e}")
        
        print("\n2. Checking assignments access...")
        try:
            assignments = list(self.canvas_course.get_assignments())
            print(f"   ✓ Can read assignments ({len(assignments)} found)")
        except Exception as e:
            print(f"   ❌ Cannot read assignments: {e}")
            return
        
        print("\n3. Testing submission access...")
        try:
            if assignments:
                test_assignment = assignments[0]
                print(f"   Testing with: {test_assignment.name}")
                
                # Try to get a submission
                enrollments = list(self.canvas_course.get_enrollments(type=['StudentEnrollment']))
                if enrollments:
                    test_student_id = enrollments[0].user['id']
                    submission = test_assignment.get_submission(test_student_id)
                    print(f"   ✓ Can read submissions")
                    
                    # Try to get current grade (this doesn't require write permission)
                    current_grade = getattr(submission, 'grade', 'N/A')
                    print(f"   ✓ Can read grades (current: {current_grade})")
                else:
                    print("   ⚠ No students enrolled to test with")
                    return
            else:
                print("   ⚠ No assignments to test with")
                return
        except Exception as e:
            print(f"   ❌ Error accessing submissions: {e}")
            return
        
        print("\n4. Checking token permissions...")
        print("   Note: To upload grades, your Canvas API token must have permission")
        print("   to modify submissions. If you're a Teacher but can't upload grades,")
        print("   you may need to regenerate your token.")
        print("\n   To regenerate your Canvas API token:")
        print("   1. Go to Canvas → Account → Settings")
        print("   2. Scroll to 'Approved Integrations'")
        print("   3. Click '+ New Access Token'")
        print("   4. Purpose: 'Grade Management'")
        print("   5. DO NOT set expiration date (or set far in future)")
        print("   6. DO NOT limit scope (leave blank for full access)")
        print("   7. Copy the token and update canvas-token.json")
        
        print("\n" + "=" * 70)
        print("If you can create assignments but not upload grades,")
        print("your token likely has limited scope. Try regenerating it.")
        print("=" * 70)
    
    def list_assignment_groups(self):
        """List all assignment groups in the course."""
        print("\n" + "=" * 70)
        print("ASSIGNMENT GROUPS")
        print("=" * 70)
        
        try:
            groups = list(self.canvas_course.get_assignment_groups())
            
            if not groups:
                print("No assignment groups found.")
                return
            
            for i, group in enumerate(groups, 1):
                weight = getattr(group, 'group_weight', 0)
                rules = getattr(group, 'rules', {})
                drop_lowest = rules.get('drop_lowest', 0) if rules else 0
                
                print(f"\n{i}. {group.name}")
                print(f"   ID: {group.id}")
                print(f"   Weight: {weight}%")
                if drop_lowest > 0:
                    print(f"   Drop lowest: {drop_lowest}")
        
        except Exception as e:
            print(f"❌ Error listing assignment groups: {e}")
    
    def list_assignments(self):
        """List all assignments in the course."""
        print("\n" + "=" * 70)
        print("ASSIGNMENTS")
        print("=" * 70)
        
        try:
            assignments = list(self.canvas_course.get_assignments())
            
            if not assignments:
                print("No assignments found.")
                return
            
            # Group by assignment group
            groups_dict = {}
            for assignment in assignments:
                group_id = getattr(assignment, 'assignment_group_id', None)
                if group_id not in groups_dict:
                    groups_dict[group_id] = []
                groups_dict[group_id].append(assignment)
            
            # Get assignment group names
            assignment_groups = {g.id: g.name for g in self.canvas_course.get_assignment_groups()}
            
            for group_id, group_assignments in groups_dict.items():
                group_name = assignment_groups.get(group_id, "Unknown Group")
                print(f"\n{group_name}:")
                for assignment in sorted(group_assignments, key=lambda a: a.name):
                    points = getattr(assignment, 'points_possible', 0)
                    published = getattr(assignment, 'published', False)
                    status = "✓" if published else "✗"
                    print(f"  {status} {assignment.name} (ID: {assignment.id}, {points} points)")
        
        except Exception as e:
            print(f"❌ Error listing assignments: {e}")
    
    def add_assignment(self):
        """Add a new assignment to a specific assignment group."""
        print("\n" + "=" * 70)
        print("ADD NEW ASSIGNMENT")
        print("=" * 70)
        
        try:
            # Get assignment groups
            groups = list(self.canvas_course.get_assignment_groups())
            
            if not groups:
                print("❌ No assignment groups found. Create groups first.")
                return
            
            # Display groups
            print("\nAvailable assignment groups:")
            for i, group in enumerate(groups, 1):
                weight = getattr(group, 'group_weight', 0)
                print(f"  {i}. {group.name} ({weight}%)")
            
            # Select group
            while True:
                group_choice = input("\nSelect assignment group (number): ").strip()
                try:
                    group_idx = int(group_choice) - 1
                    if 0 <= group_idx < len(groups):
                        selected_group = groups[group_idx]
                        break
                    else:
                        print("❌ Invalid number. Try again.")
                except ValueError:
                    print("❌ Please enter a number.")
            
            print(f"\nSelected group: {selected_group.name}")
            
            # Get assignment details
            name = input("\nAssignment name: ").strip()
            if not name:
                print("❌ Assignment name cannot be empty.")
                return
            
            points_str = input("Points possible: ").strip()
            try:
                points_possible = float(points_str)
            except ValueError:
                print("❌ Invalid points value.")
                return
            
            # Optional: due date
            due_date = input("Due date (YYYY-MM-DD HH:MM or leave blank): ").strip()
            
            # Optional: description
            description = input("Description (optional): ").strip()
            
            # Submission types
            print("\nSubmission types:")
            print("  1. online_upload (file upload)")
            print("  2. online_text_entry (text entry)")
            print("  3. online_url (URL)")
            print("  4. none (no submission)")
            submission_choice = input("Select submission type (1-4): ").strip()
            
            submission_types_map = {
                "1": ["online_upload"],
                "2": ["online_text_entry"],
                "3": ["online_url"],
                "4": ["none"]
            }
            submission_types = submission_types_map.get(submission_choice, ["none"])
            
            # Ask about publishing
            print("\nPublish assignment?")
            print("  Note: Unpublished assignments typically cannot receive grades")
            publish_choice = input("Publish now? (Y/n): ").strip().lower()
            publish = publish_choice != 'n'  # Default to yes
            
            # Confirm
            print("\n" + "-" * 70)
            print("Assignment details:")
            print(f"  Name: {name}")
            print(f"  Group: {selected_group.name}")
            print(f"  Points: {points_possible}")
            if due_date:
                print(f"  Due: {due_date}")
            print(f"  Submission type: {submission_types[0]}")
            if description:
                print(f"  Description: {description}")
            print(f"  Published: {'Yes' if publish else 'No (draft)'}")
            print("-" * 70)
            
            confirm = input("\nCreate this assignment? (y/n): ").strip().lower()
            if confirm != 'y':
                print("❌ Cancelled.")
                return
            
            # Create assignment
            assignment_config = {
                "name": name,
                "points_possible": points_possible,
                "assignment_group_id": selected_group.id,
                "submission_types": submission_types,
                "grading_type": "points",
                "published": publish,
            }
            
            if due_date:
                assignment_config["due_at"] = due_date
            if description:
                assignment_config["description"] = description
            
            print("\nCreating assignment...")
            assignment = self.canvas_course.create_assignment(assignment=assignment_config)
            
            print(f"✅ Assignment created successfully!")
            print(f"   ID: {assignment.id}")
            print(f"   Name: {assignment.name}")
            print(f"   Status: {'Published' if publish else 'Unpublished (draft)'}")
            
            if not publish:
                print("\n⚠  Note: This assignment is unpublished and cannot receive grades yet.")
                print("   You can publish it later in Canvas or use this script again.")
        
        except Exception as e:
            print(f"❌ Error creating assignment: {e}")
    
    def publish_assignment(self):
        """Publish or unpublish an assignment."""
        print("\n" + "=" * 70)
        print("PUBLISH/UNPUBLISH ASSIGNMENT")
        print("=" * 70)
        
        try:
            # Get assignments
            assignments = list(self.canvas_course.get_assignments())
            
            if not assignments:
                print("❌ No assignments found.")
                return
            
            # Display assignments with published status
            print("\nAvailable assignments:")
            for i, assignment in enumerate(assignments, 1):
                published = getattr(assignment, 'published', False)
                status = "✓ Published" if published else "✗ Unpublished"
                points = getattr(assignment, 'points_possible', 0)
                print(f"  {i}. {assignment.name} ({points} pts) - {status}")
            
            # Select assignment
            while True:
                assignment_choice = input("\nSelect assignment (number) or enter assignment ID: ").strip()
                try:
                    # Try as index first
                    if assignment_choice.isdigit() and int(assignment_choice) <= len(assignments):
                        assignment_idx = int(assignment_choice) - 1
                        if 0 <= assignment_idx < len(assignments):
                            selected_assignment = assignments[assignment_idx]
                            break
                    # Try as assignment ID
                    assignment_id = int(assignment_choice)
                    selected_assignment = self.canvas_course.get_assignment(assignment_id)
                    break
                except (ValueError, Exception) as e:
                    print(f"❌ Invalid selection: {e}")
            
            current_status = getattr(selected_assignment, 'published', False)
            print(f"\nSelected: {selected_assignment.name}")
            print(f"Current status: {'Published' if current_status else 'Unpublished'}")
            
            # Ask what to do
            if current_status:
                action = input("\nUnpublish this assignment? (y/n): ").strip().lower()
                new_status = action != 'y'
            else:
                action = input("\nPublish this assignment? (Y/n): ").strip().lower()
                new_status = action != 'n'
            
            if new_status == current_status:
                print("❌ No change requested.")
                return
            
            # Update assignment
            print(f"\n{'Publishing' if new_status else 'Unpublishing'} assignment...")
            selected_assignment.edit(assignment={'published': new_status})
            
            print(f"✅ Assignment {'published' if new_status else 'unpublished'} successfully!")
            
            if new_status:
                print("   Students can now see this assignment and submit work.")
                print("   You can now upload grades for this assignment.")
            else:
                print("   Assignment is now hidden from students.")
        
        except Exception as e:
            print(f"❌ Error updating assignment: {e}")
    
    def upload_grades(self):
        """Upload grades for an assignment."""
        print("\n" + "=" * 70)
        print("UPLOAD GRADES")
        print("=" * 70)
        
        # Check if user has grading permissions
        print("\nChecking permissions...")
        try:
            enrollments = list(self.canvas_course.get_enrollments(
                type=['TeacherEnrollment', 'TaEnrollment'],
                user_id='self'
            ))
            
            if not enrollments:
                print("⚠ Warning: You don't appear to have Teacher or TA enrollment.")
                print("  You may not be able to upload grades.")
                print("  If uploads fail, you may need to regenerate your API token.")
                proceed = input("\nContinue anyway? (y/n): ").strip().lower()
                if proceed != 'y':
                    return
            else:
                print("✓ Permission check passed")
        except Exception as e:
            print(f"⚠ Warning: Could not verify permissions - {e}")
            print("  Attempting to continue anyway...")
        
        try:
            # Get assignments
            assignments = list(self.canvas_course.get_assignments())
            
            if not assignments:
                print("❌ No assignments found.")
                return
            
            # Display assignments
            print("\nAvailable assignments:")
            for i, assignment in enumerate(assignments, 1):
                points = getattr(assignment, 'points_possible', 0)
                print(f"  {i}. {assignment.name} ({points} points, ID: {assignment.id})")
            
            # Select assignment
            while True:
                assignment_choice = input("\nSelect assignment (number) or enter assignment ID: ").strip()
                try:
                    # Try as index first
                    if assignment_choice.isdigit() and int(assignment_choice) <= len(assignments):
                        assignment_idx = int(assignment_choice) - 1
                        if 0 <= assignment_idx < len(assignments):
                            selected_assignment = assignments[assignment_idx]
                            break
                    # Try as assignment ID
                    assignment_id = int(assignment_choice)
                    selected_assignment = self.canvas_course.get_assignment(assignment_id)
                    break
                except (ValueError, Exception) as e:
                    print(f"❌ Invalid selection: {e}")
            
            print(f"\nSelected assignment: {selected_assignment.name}")
            print(f"Points possible: {getattr(selected_assignment, 'points_possible', 0)}")
            
            # Choose input method
            print("\nGrade input methods:")
            print("  1. CSV file (flexible format: supports MIT ID, Canvas ID, with optional Name column)")
            print("  2. Manual entry (interactive)")
            method = input("\nSelect method (1-2): ").strip()
            
            if method == "1":
                self._upload_grades_from_csv(selected_assignment)
            elif method == "2":
                self._upload_grades_manual(selected_assignment)
            else:
                print("❌ Invalid method.")
        
        except Exception as e:
            print(f"❌ Error uploading grades: {e}")
    
    def _upload_grades_from_csv(self, assignment):
        """Upload grades from a CSV file."""
        csv_path = input("\nEnter CSV file path: ").strip()
        
        if not Path(csv_path).exists():
            print(f"❌ File not found: {csv_path}")
            return
        
        print("\nReading CSV file...")
        print("Detecting CSV format...")
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames
                
                if not fieldnames:
                    print("❌ CSV file is empty or has no headers.")
                    return
                
                print(f"Found columns: {', '.join(fieldnames)}")
                
                # Detect format and find the grade column
                grade_col = None
                id_col = None
                name_col = None
                
                # Look for MIT ID column (case insensitive)
                for col in fieldnames:
                    col_lower = col.lower().strip()
                    if 'mit' in col_lower and 'id' in col_lower:
                        id_col = col
                    elif col_lower in ['student_id', 'id', 'canvas_id', 'user_id']:
                        if id_col is None:  # MIT ID takes precedence
                            id_col = col
                    elif col_lower in ['name', 'student', 'student name']:
                        name_col = col
                
                # Look for grade column (last column or one with grade-like name)
                for col in fieldnames:
                    col_lower = col.lower().strip()
                    if any(keyword in col_lower for keyword in ['grade', 'score', 'points', 'percent', 'attendance']):
                        grade_col = col
                        break
                
                # If no grade column found by keyword, use last column
                if grade_col is None:
                    grade_col = fieldnames[-1]
                    print(f"Using last column as grade: '{grade_col}'")
                
                if not id_col:
                    print("❌ Could not identify student ID column.")
                    print("    Expected column names like: 'MIT ID', 'student_id', 'id'")
                    return
                
                print(f"Using ID column: '{id_col}'")
                print(f"Using grade column: '{grade_col}'")
                if name_col:
                    print(f"Using name column: '{name_col}'")
            
            # Build student lookup by MIT ID (sis_user_id)
            print("\nBuilding student lookup table...")
            mit_id_to_canvas_id = {}
            
            enrollments = list(self.canvas_course.get_enrollments(type=['StudentEnrollment']))
            for enrollment in enrollments:
                user = enrollment.user
                canvas_id = user.get('id')
                sis_id = user.get('sis_user_id')  # This is the MIT ID
                
                if sis_id and canvas_id:
                    mit_id_to_canvas_id[str(sis_id).strip()] = canvas_id
            
            print(f"Found {len(mit_id_to_canvas_id)} students with MIT IDs")
            
            # Read grades from CSV
            grades = []
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    student_id = row[id_col].strip()
                    grade = row[grade_col].strip()
                    name = row.get(name_col, '').strip() if name_col else ''
                    
                    if not student_id or not grade:
                        continue
                    
                    # Try to find Canvas user ID
                    canvas_id = None
                    
                    # First try as MIT ID (sis_user_id)
                    if student_id in mit_id_to_canvas_id:
                        canvas_id = mit_id_to_canvas_id[student_id]
                    else:
                        # Try as Canvas ID directly
                        try:
                            canvas_id = int(student_id)
                        except ValueError:
                            print(f"  ⚠ Warning: Could not find student with ID '{student_id}' {f'({name})' if name else ''}")
                            continue
                    
                    grades.append((canvas_id, grade, name or student_id))
            
            if not grades:
                print("❌ No valid grades found in CSV.")
                return
            
            print(f"\nFound {len(grades)} grades to upload.")
            print("Preview:")
            for canvas_id, grade, identifier in grades[:5]:
                print(f"  {identifier}: {grade}")
            if len(grades) > 5:
                print(f"  ... and {len(grades) - 5} more")
            
            confirm = input("\nUpload these grades? (y/n): ").strip().lower()
            if confirm != 'y':
                print("❌ Cancelled.")
                return
            
            # Upload grades
            print("\nUploading grades...")
            success_count = 0
            error_count = 0
            
            for canvas_id, grade, identifier in grades:
                try:
                    submission = assignment.get_submission(canvas_id)
                    # Try the primary method: edit submission with posted_grade
                    submission.edit(submission={'posted_grade': grade})
                    success_count += 1
                    print(f"  ✅ {identifier}: {grade}")
                except Exception as e:
                    error_count += 1
                    error_msg = str(e)
                    
                    # Show full error on first failure for debugging
                    if error_count == 1:
                        print(f"\n  ❌ First error details: {error_msg}")
                        print(f"     Error type: {type(e).__name__}")
                    
                    if 'unauthorized' in error_msg.lower() or 'permission' in error_msg.lower():
                        print(f"  ❌ {identifier}: Permission denied")
                        if error_count == 1:
                            print("\n💡 Possible causes:")
                            print("   1. Assignment may have 'muted' or 'anonymous' grading enabled")
                            print("   2. Assignment may require posting grades separately")
                            print("   3. Canvas API token permissions (try regenerating)")
                            print("   4. Assignment may be locked or past due with restrictions")
                            return
                    else:
                        print(f"  ❌ {identifier}: {error_msg}")
            
            print(f"\n✅ Upload complete!")
            print(f"   Successful: {success_count}")
            print(f"   Errors: {error_count}")
        
        except Exception as e:
            print(f"❌ Error reading CSV: {e}")
    
    def _upload_grades_manual(self, assignment):
        """Upload grades manually (interactive)."""
        print("\nFetching students...")
        
        try:
            # Get students (active enrollments)
            enrollments = list(self.canvas_course.get_enrollments(type=['StudentEnrollment']))
            students = [e for e in enrollments if getattr(e, 'enrollment_state', '') == 'active']
            
            if not students:
                print("❌ No active students found.")
                return
            
            print(f"\nFound {len(students)} active students.")
            print("\nEnter grades for each student (or press Enter to skip):")
            
            grades_to_upload = []
            
            for enrollment in students:
                user = enrollment.user
                student_name = user.get('name', 'Unknown')
                student_id = user.get('id')
                
                grade = input(f"  {student_name} (ID: {student_id}): ").strip()
                
                if grade:
                    try:
                        # Validate it's a number
                        float(grade)
                        grades_to_upload.append((student_id, grade))
                    except ValueError:
                        print(f"    ⚠ Invalid grade (skipped)")
            
            if not grades_to_upload:
                print("\n❌ No grades entered.")
                return
            
            print(f"\n{len(grades_to_upload)} grades entered.")
            confirm = input("\nUpload these grades? (y/n): ").strip().lower()
            if confirm != 'y':
                print("❌ Cancelled.")
                return
            
            # Upload grades
            print("\nUploading grades...")
            success_count = 0
            error_count = 0
            
            for student_id, grade in grades_to_upload:
                try:
                    submission = assignment.get_submission(student_id)
                    submission.edit(submission={'posted_grade': grade})
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    error_msg = str(e)
                    
                    # Show full error on first failure for debugging
                    if error_count == 1:
                        print(f"\n  ❌ First error details: {error_msg}")
                        print(f"     Error type: {type(e).__name__}")
                    
                    if 'unauthorized' in error_msg.lower() or 'permission' in error_msg.lower():
                        print(f"  ❌ Student {student_id}: Permission denied")
                        if error_count == 1:
                            print("\n💡 Possible causes:")
                            print("   1. Assignment may have 'muted' or 'anonymous' grading enabled")
                            print("   2. Assignment may require posting grades separately")
                            print("   3. Canvas API token permissions (try regenerating)")
                            print("   4. Assignment may be locked or past due with restrictions")
                            return
                    else:
                        print(f"  ❌ Student {student_id}: {error_msg}")
            
            print(f"\n✅ Upload complete!")
            print(f"   Successful: {success_count}")
            print(f"   Errors: {error_count}")
        
        except Exception as e:
            print(f"❌ Error in manual grade entry: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Interactive assignment and grade management for Canvas"
    )
    parser.add_argument(
        "--course-id",
        type=int,
        help="Canvas course ID (if not provided, you'll be prompted to select)"
    )
    args = parser.parse_args()
    
    try:
        # Connect to Canvas
        print("Connecting to Canvas...")
        conn = CanvasConnection()
        
        # Get course
        course = Course.from_args(conn, args.course_id)
        
        # Create manager and show menu
        manager = AssignmentManager(conn, course)
        manager.show_menu()
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
