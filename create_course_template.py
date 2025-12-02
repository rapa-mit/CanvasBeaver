#!/usr/bin/env python3
"""
create_course_template.py
--------------------------------
Comprehensive example of using Canvas API to:
- Create/configure a course
- Set up assignment groups with weights and drop rules
- Create assignments
- Set up grading standards
- Enroll users

This script demonstrates the full capability of the Canvas API for
course administration. Some operations require admin privileges.

Usage:
  # Show what the script would do (dry-run)
  python3 create_course_template.py --dry-run
  
  # Actually create/configure a course
  python3 create_course_template.py --course-id 12345
  
  # Create assignment groups only
  python3 create_course_template.py --course-id 12345 --setup-groups-only

WARNING: This script MODIFIES Canvas. Use with caution!
"""
from __future__ import annotations

import argparse
from typing import Dict, List, Any, Optional
from canvas.connection import CanvasConnection


class CourseBuilder:
    """Build and configure Canvas courses programmatically."""
    
    def __init__(self, canvas_connection: CanvasConnection, dry_run: bool = True):
        self.conn = canvas_connection
        self.canvas = canvas_connection.get_canvas()
        self.dry_run = dry_run
        
    def create_course(self, account_id: int, course_config: Dict[str, Any]) -> Optional[Any]:
        """Create a new course.
        
        Requires: Account admin privileges
        
        Args:
            account_id: Canvas account ID (usually 1 for root)
            course_config: Course configuration dict
            
        Returns:
            Course object or None if dry_run
        """
        print(f"\n{'[DRY RUN] ' if self.dry_run else ''}Creating course...")
        print(f"  Name: {course_config.get('name', 'Unnamed')}")
        print(f"  Course Code: {course_config.get('course_code', 'N/A')}")
        
        if self.dry_run:
            print("  → Skipped (dry-run mode)")
            return None
        
        try:
            account = self.canvas.get_account(account_id)
            course = account.create_course(course=course_config)
            print(f"  ✓ Created course ID: {course.id}")
            return course
        except Exception as e:
            print(f"  ✗ Error: {e}")
            return None
    
    def configure_course_settings(self, course_id: int, settings: Dict[str, Any]) -> bool:
        """Configure course settings.
        
        Args:
            course_id: Canvas course ID
            settings: Settings dictionary
            
        Returns:
            True if successful
        """
        print(f"\n{'[DRY RUN] ' if self.dry_run else ''}Configuring course settings...")
        
        for key, value in settings.items():
            print(f"  {key}: {value}")
        
        if self.dry_run:
            print("  → Skipped (dry-run mode)")
            return True
        
        try:
            course = self.canvas.get_course(course_id)
            
            # Update course settings
            if 'name' in settings or 'course_code' in settings:
                course.update(course=settings)
            
            # Update course-level settings
            course_settings = {}
            if 'allow_student_discussion_topics' in settings:
                course_settings['allow_student_discussion_topics'] = settings['allow_student_discussion_topics']
            if 'hide_final_grades' in settings:
                course_settings['hide_final_grades'] = settings['hide_final_grades']
            
            if course_settings:
                course.update_settings(**course_settings)
            
            print("  ✓ Course settings updated")
            return True
        except Exception as e:
            print(f"  ✗ Error: {e}")
            return False
    
    def setup_assignment_groups(
        self,
        course_id: int,
        groups: List[Dict[str, Any]],
        use_weighted: bool = True
    ) -> List[Any]:
        """Create assignment groups with weights and drop rules.
        
        Args:
            course_id: Canvas course ID
            groups: List of group configurations
            use_weighted: Enable weighted assignment groups
            
        Returns:
            List of created assignment group objects
        """
        print(f"\n{'[DRY RUN] ' if self.dry_run else ''}Setting up assignment groups...")
        print(f"  Weighted grading: {use_weighted}")
        
        created_groups = []
        
        for group_config in groups:
            print(f"\n  {group_config['name']}:")
            print(f"    Weight: {group_config.get('group_weight', 0)}%")
            if 'rules' in group_config and group_config['rules']:
                print(f"    Rules: {group_config['rules']}")
        
        if self.dry_run:
            print("\n  → Skipped (dry-run mode)")
            return []
        
        try:
            course = self.canvas.get_course(course_id)
            
            # Enable weighted assignment groups
            if use_weighted:
                course.update(course={'apply_assignment_group_weights': True})
                print("  ✓ Enabled weighted assignment groups")
            
            # Create each assignment group
            for group_config in groups:
                ag = course.create_assignment_group(**group_config)
                created_groups.append(ag)
                print(f"  ✓ Created: {ag.name} (ID: {ag.id})")
            
            return created_groups
        except Exception as e:
            print(f"  ✗ Error: {e}")
            return []
    
    def create_assignments(
        self,
        course_id: int,
        assignments: List[Dict[str, Any]]
    ) -> List[Any]:
        """Create assignments.
        
        Args:
            course_id: Canvas course ID
            assignments: List of assignment configurations
            
        Returns:
            List of created assignment objects
        """
        print(f"\n{'[DRY RUN] ' if self.dry_run else ''}Creating assignments...")
        
        for assignment_config in assignments:
            print(f"  {assignment_config.get('name', 'Unnamed')}:")
            print(f"    Points: {assignment_config.get('points_possible', 0)}")
            print(f"    Group ID: {assignment_config.get('assignment_group_id', 'N/A')}")
        
        if self.dry_run:
            print("  → Skipped (dry-run mode)")
            return []
        
        created_assignments = []
        
        try:
            course = self.canvas.get_course(course_id)
            
            for assignment_config in assignments:
                assignment = course.create_assignment(assignment=assignment_config)
                created_assignments.append(assignment)
                print(f"  ✓ Created: {assignment.name} (ID: {assignment.id})")
            
            return created_assignments
        except Exception as e:
            print(f"  ✗ Error: {e}")
            return []
    
    def setup_grading_standard(
        self,
        course_id: int,
        title: str,
        grading_scheme: List[tuple]
    ) -> Optional[Any]:
        """Create a grading standard (letter grade scale).
        
        Args:
            course_id: Canvas course ID
            title: Grading standard title
            grading_scheme: List of (name, value) tuples
                           e.g., [("A", 0.93), ("A-", 0.90), ...]
            
        Returns:
            Grading standard object or None
        """
        print(f"\n{'[DRY RUN] ' if self.dry_run else ''}Setting up grading standard...")
        print(f"  Title: {title}")
        print(f"  Scheme:")
        for name, value in grading_scheme:
            print(f"    {name}: {value*100}%")
        
        if self.dry_run:
            print("  → Skipped (dry-run mode)")
            return None
        
        try:
            course = self.canvas.get_course(course_id)
            
            # Canvas API expects grading_scheme_entry format
            scheme_entries = [
                {"name": name, "value": value}
                for name, value in grading_scheme
            ]
            
            # Note: create_grading_standard might not be available on all Canvas instances
            # This is a Canvas account-level feature
            grading_std = course.create_grading_standard(
                title=title,
                grading_scheme_entry=scheme_entries
            )
            
            print(f"  ✓ Created grading standard (ID: {grading_std.id})")
            return grading_std
        except Exception as e:
            print(f"  ✗ Error: {e}")
            print("  Note: Grading standards may require admin privileges")
            return None
    
    def enroll_users(
        self,
        course_id: int,
        enrollments: List[Dict[str, Any]]
    ) -> List[Any]:
        """Enroll users in the course.
        
        Args:
            course_id: Canvas course ID
            enrollments: List of enrollment configs
                        [{"user_id": 123, "type": "StudentEnrollment"}, ...]
            
        Returns:
            List of created enrollment objects
        """
        print(f"\n{'[DRY RUN] ' if self.dry_run else ''}Enrolling users...")
        
        for enrollment in enrollments:
            print(f"  User {enrollment.get('user_id')}: {enrollment.get('type')}")
        
        if self.dry_run:
            print("  → Skipped (dry-run mode)")
            return []
        
        created_enrollments = []
        
        try:
            course = self.canvas.get_course(course_id)
            
            for enrollment_config in enrollments:
                enrollment = course.enroll_user(
                    user=enrollment_config['user_id'],
                    enrollment={"type": enrollment_config['type']}
                )
                created_enrollments.append(enrollment)
                print(f"  ✓ Enrolled user {enrollment_config['user_id']}")
            
            return created_enrollments
        except Exception as e:
            print(f"  ✗ Error: {e}")
            return []


def example_course_setup():
    """Example configuration for a complete course setup."""
    
    # Course configuration
    course_config = {
        "name": "Example Course - Unified Engineering",
        "course_code": "16.001",
        "time_zone": "America/New_York",
        "apply_assignment_group_weights": True,
        "hide_final_grades": True,
    }
    
    # Assignment groups with weights and drop rules
    assignment_groups = [
        {
            "name": "Problem Sets",
            "group_weight": 15.0,
            "rules": {
                "drop_lowest": 1,
            }
        },
        {
            "name": "Quizlets",
            "group_weight": 25.0,
            "rules": {
                "drop_lowest": 1,
            }
        },
        {
            "name": "Midterm",
            "group_weight": 25.0,
        },
        {
            "name": "Final Exam",
            "group_weight": 35.0,
        }
    ]
    
    # Sample assignments (after groups are created)
    # Note: assignment_group_id must be filled in after creating groups
    assignments_template = [
        {
            "name": "Problem Set #1",
            "points_possible": 100,
            "submission_types": ["online_upload"],
            "grading_type": "points",
            # "assignment_group_id": <will be set after group creation>
        },
        {
            "name": "Quizlet #1",
            "points_possible": 10,
            "submission_types": ["online_quiz"],
            "grading_type": "points",
        },
    ]
    
    # MIT-style grading standard
    grading_standard = [
        ("A", 0.90),
        ("B", 0.80),
        ("C", 0.70),
        ("D", 0.60),
        ("F", 0.00),
    ]
    
    return {
        "course_config": course_config,
        "assignment_groups": assignment_groups,
        "assignments_template": assignments_template,
        "grading_standard": grading_standard,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Create and configure Canvas course via API"
    )
    parser.add_argument("--course-id", type=int, help="Existing course ID to configure")
    parser.add_argument("--create-new", action="store_true",
                       help="Create a new course (requires admin)")
    parser.add_argument("--account-id", type=int, default=1,
                       help="Account ID for new course creation")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be done without making changes")
    parser.add_argument("--setup-groups-only", action="store_true",
                       help="Only set up assignment groups")
    args = parser.parse_args()
    
    # Default to dry-run if no course specified
    if not args.course_id and not args.create_new:
        print("No course specified. Running in dry-run mode to show example.\n")
        args.dry_run = True
    
    print("=" * 70)
    print("Canvas Course Builder")
    print("=" * 70)
    
    if args.dry_run:
        print("\n⚠  DRY-RUN MODE: No changes will be made to Canvas")
    
    # Connect to Canvas
    print("\nConnecting to Canvas...")
    conn = CanvasConnection()
    builder = CourseBuilder(conn, dry_run=args.dry_run)
    
    # Get example configuration
    config = example_course_setup()
    
    # Create or get course
    course_id = args.course_id
    
    if args.create_new:
        print("\n" + "=" * 70)
        print("CREATING NEW COURSE")
        print("=" * 70)
        course = builder.create_course(args.account_id, config["course_config"])
        if course:
            course_id = course.id
    
    if not course_id and not args.dry_run:
        print("\nError: No course ID specified and course creation failed.")
        print("Use --course-id ID or --create-new with --account-id")
        return 1
    
    if args.dry_run:
        course_id = 99999  # Dummy ID for dry-run
        print(f"\nUsing example course ID: {course_id}")
    
    # Configure course settings
    if not args.setup_groups_only:
        print("\n" + "=" * 70)
        print("CONFIGURING COURSE SETTINGS")
        print("=" * 70)
        builder.configure_course_settings(course_id, config["course_config"])
    
    # Setup assignment groups
    print("\n" + "=" * 70)
    print("SETTING UP ASSIGNMENT GROUPS")
    print("=" * 70)
    groups = builder.setup_assignment_groups(
        course_id,
        config["assignment_groups"],
        use_weighted=True
    )
    
    if args.setup_groups_only:
        print("\n" + "=" * 70)
        print("Done! (groups only)")
        return 0
    
    # Create sample assignments
    if groups and not args.dry_run:
        print("\n" + "=" * 70)
        print("CREATING SAMPLE ASSIGNMENTS")
        print("=" * 70)
        
        # Set assignment group IDs
        assignments = config["assignments_template"]
        if len(assignments) > 0 and len(groups) > 0:
            assignments[0]["assignment_group_id"] = groups[0].id  # Problem Set
        if len(assignments) > 1 and len(groups) > 1:
            assignments[1]["assignment_group_id"] = groups[1].id  # Quizlet
        
        builder.create_assignments(course_id, assignments)
    
    # Setup grading standard
    print("\n" + "=" * 70)
    print("SETTING UP GRADING STANDARD")
    print("=" * 70)
    builder.setup_grading_standard(
        course_id,
        "MIT Letter Grades",
        config["grading_standard"]
    )
    
    # Example enrollments (commented out - requires user IDs)
    # print("\n" + "=" * 70)
    # print("ENROLLING USERS")
    # print("=" * 70)
    # enrollments = [
    #     {"user_id": 12345, "type": "StudentEnrollment"},
    #     {"user_id": 67890, "type": "TeacherEnrollment"},
    # ]
    # builder.enroll_users(course_id, enrollments)
    
    print("\n" + "=" * 70)
    print("COMPLETE!")
    print("=" * 70)
    
    if args.dry_run:
        print("\nThis was a dry-run. To actually create/configure:")
        print("  python3 create_course_template.py --course-id YOUR_COURSE_ID")
        print("\nOr to create a new course (requires admin):")
        print("  python3 create_course_template.py --create-new --account-id 1")


if __name__ == "__main__":
    main()
