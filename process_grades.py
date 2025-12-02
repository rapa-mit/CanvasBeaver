#!/usr/bin/env python3
"""
process_grades.py
--------------------------------
Process and analyze course grades with advanced features:
- Configurable grade type weights
- Drop lowest grades by type
- Letter grade computation
- Anomaly detection
- Individual and summary reports
- Partial semester grading (excludes ungraded assignments by default)

Usage:
  python3 process_grades.py --config CONFIG_FILE [--course-id ID] [options]
  
The --config argument is REQUIRED to specify drop_lowest settings.
Recommended: --config grade_config_canvas.yaml

Caching:
  Gradebook data is automatically cached to speed up repeated runs.
  Cache files are named: gradebook_<course_id>_<date>.pkl
  If a cache exists, you'll be prompted to use it or download fresh data.
  Use --no-cache to always download fresh data from Canvas.

By default, only graded assignments are included in grade calculations.
This provides accurate "current grade" based on work completed so far.
Use --include-ungraded to include all assignments (treating ungraded as zeros).
"""
from __future__ import annotations

import argparse
import yaml
from pathlib import Path
from typing import Dict, Any

from canvas.connection import CanvasConnection
from canvas.course import Course
from canvas.gradebook import get_course_gradebook
from canvas.grade_processor import GradeConfiguration, GradeProcessor
from canvas.assignment import AssignmentGroup


def load_config(config_file: str) -> Dict[str, Any]:
    """Load grade processing configuration from YAML file.

    Expected format (option 1 - use Canvas weights):
    use_canvas_groups: true
    drop_lowest:
      Homework: 1
      Quizzes: 1
    letter_grade_scale: MIT-letter-grades.yaml  # optional
    
    Expected format (option 2 - manual weights):
    use_canvas_groups: false
    grade_types:
      Problem Set: 0.15
      Quizlet: 0.25
      Midterm: 0.25
      Final: 0.35
    drop_lowest:
      Problem Set: 1
      Quizlet: 1
    allow_partial: false
    letter_grade_scale: MIT-letter-grades.yaml  # optional
    """
    with open(config_file, 'r') as f:
        return yaml.safe_load(f)


def save_csv_report(processor: GradeProcessor, filename: str = 'grades_summary.csv') -> None:
    """Save grades to CSV format."""
    import csv
    
    students = processor.get_sorted_students(by='name')
    
    # Determine columns
    fieldnames = ['Name', 'Email', 'MIT ID']
    
    # Add grade type columns
    if students:
        for type_name in students[0].grade_types.keys():
            fieldnames.append(type_name)
    
    fieldnames.extend(['Total %', 'Letter Grade', 'Alerts'])
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for student in students:
            row = {
                'Name': student.name,
                'Email': student.email or '',
                'MIT ID': student.mit_id or '',
                'Total %': f"{student.normalized_percentage * 100:.2f}",
                'Letter Grade': student.letter_grade,
                'Alerts': 'YES' if student.anomalies else '',
            }
            
            # Add grade type percentages
            for type_name, result in student.grade_types.items():
                row[type_name] = f"{result.average_percentage * 100:.2f}"
            
            writer.writerow(row)
    
    print(f"Saved CSV summary to {filename}")


def save_anomaly_report(processor: GradeProcessor, filename: str = 'anomaly_report.txt') -> None:
    """Save detailed anomaly report."""
    flagged = [s for s in processor.processed_students.values() if s.anomalies]
    
    if not flagged:
        print("No anomalies detected - skipping anomaly report")
        return
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("GRADE PATTERN ANOMALY REPORT\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Total students flagged: {len(flagged)}\n\n")
        
        # Sort by name
        flagged.sort(key=lambda s: s.name)
        
        for student in flagged:
            f.write("-" * 80 + "\n")
            f.write(f"Student: {student.name}\n")
            if student.email:
                f.write(f"Email: {student.email}\n")
            f.write(f"Overall Grade: {student.normalized_percentage*100:.2f}% = {student.letter_grade}\n")
            f.write("\nGrade Breakdown:\n")
            
            for type_name, result in student.grade_types.items():
                f.write(f"  {type_name}: {result.average_percentage*100:.2f}%\n")
            
            f.write("\nAlerts:\n")
            for anomaly in student.anomalies:
                f.write(f"  ⚠ {anomaly}\n")
            f.write("\n")
        
        f.write("=" * 80 + "\n")
    
    print(f"Saved anomaly report to {filename}")


def print_grade_list(processor: GradeProcessor, sort_by: str = 'name') -> None:
    """Print formatted list of grades."""
    students = processor.get_sorted_students(by=sort_by)
    
    print(f"\n{'='*70}")
    print(f"FINAL GRADES (sorted by {sort_by})")
    print(f"{'='*70}")
    
    for student in students:
        alert = " ⚠" if student.anomalies else ""
        print(f"{student.name:40s} {student.normalized_percentage*100:6.2f}% = {student.letter_grade:3s}{alert}")


def main():
    parser = argparse.ArgumentParser(description="Process Canvas course grades")
    parser.add_argument("--course-id", type=int, help="Canvas course ID (optional)")
    parser.add_argument("--config", type=str, help="Configuration YAML file")
    parser.add_argument("--include-inactive", action="store_true", help="Include inactive enrollments")
    parser.add_argument("--output-dir", type=str, help="Output directory for reports (default: {course}-{date})")
    parser.add_argument("--include-ungraded", action="store_true", 
                       help="Include ungraded assignments (default: only count graded work)")
    parser.add_argument("--no-cache", action="store_true", help="Skip cache, always download fresh from Canvas")
    args = parser.parse_args()

    # Load configuration
    if args.config:
        config_data = load_config(args.config)
    else:
        # Default: use Canvas assignment groups
        print("Warning: No config file specified, will use Canvas assignment group weights")
        config_data = {
            "use_canvas_groups": True,
            "drop_lowest": {},
        }

    # Connect to Canvas to get course info
    print("Connecting to Canvas...")
    conn = CanvasConnection()
    course = Course.from_args(conn, args.course_id)
    course_id = course.course_id
    course_code = course.course_code  # e.g., "16.001"
    
    # Find latest cache file for this course
    from pathlib import Path
    from datetime import datetime
    import glob
    import os
    
    cache_pattern = f"gradebook_{course_id}_*.pkl"
    cache_files = sorted(glob.glob(cache_pattern), reverse=True)  # newest first
    
    use_cache = False
    if cache_files and not args.no_cache:
        # Found cache file(s), ask user if they want to use it
        latest_cache = cache_files[0]
        cache_time = os.path.getmtime(latest_cache)
        cache_date = datetime.fromtimestamp(cache_time).strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"\nFound cached gradebook: {latest_cache}")
        print(f"  Downloaded: {cache_date}")
        response = input("Use cached data? (Y/n): ").strip().lower()
        use_cache = response != 'n'
    
    # Load gradebook (from cache or Canvas)
    if use_cache:
        print(f"Loading gradebook from cache: {latest_cache}")
        from canvas.gradebook import Gradebook
        gb = Gradebook.load_from_cache(latest_cache)
    else:
        # Download from Canvas
        print(f"Loading gradebook for: {course.name}")
        gb = get_course_gradebook(conn, course_id, include_inactive=args.include_inactive)
        
        print(f"Loaded {len(gb.get_students())} students, {len(gb.get_assignments())} assignments")
        
        # Always save to cache with course_id and date
        today = datetime.now().strftime("%Y%m%d")
        cache_file = f"gradebook_{course_id}_{today}.pkl"
        gb.save_to_cache(cache_file)

    # Get letter grade scale (optional)
    letter_grade_scale = config_data.get('letter_grade_scale', None)

    # Determine if we use Canvas groups or manual configuration
    use_canvas_groups = config_data.get('use_canvas_groups', True)

    if use_canvas_groups:
        # Fetch assignment groups from Canvas
        print("\nFetching assignment groups from Canvas...")
        canvas_course = conn.get_canvas().get_course(course.course_id)
        
        # Check if course uses weighted groups
        uses_weights = getattr(canvas_course, 'apply_assignment_group_weights', False)
        if not uses_weights:
            print("WARNING: Course does not have 'apply_assignment_group_weights' enabled in Canvas.")
            print("         Grade weights may not be configured. Proceeding anyway...")
        
        assignment_groups = list(canvas_course.get_assignment_groups())
        print(f"Found {len(assignment_groups)} assignment groups:")
        for g in assignment_groups:
            weight = getattr(g, 'group_weight', 0)
            print(f"  - {g.name}: {weight}%")
        
        # Create processor with Canvas groups
        processor = GradeProcessor(
            gradebook=gb,
            assignment_groups=assignment_groups,
            letter_grade_scale=letter_grade_scale,
        )
    else:
        # Use manual configuration (legacy mode)
        print("\nUsing manual grade type configuration from config file...")
        grade_config = GradeConfiguration(
            grade_types=config_data['grade_types'],
            allow_partial=config_data.get('allow_partial', False),
        )
        
        # Create processor with manual config
        processor = GradeProcessor(
            gradebook=gb,
            grade_config=grade_config,
            letter_grade_scale=letter_grade_scale,
        )

    # Process grades
    print("\nProcessing grades...")
    processor.process_grades(
        drop_lowest=config_data.get('drop_lowest', {}),
        detect_anomalies=True,
        only_graded=not args.include_ungraded,  # By default, only count graded work
    )

    # Print summary statistics
    processor.print_summary()
    
    # Print grading mode
    if not args.include_ungraded:
        print("\n" + "=" * 70)
        print("NOTE: Grades computed based on GRADED ASSIGNMENTS ONLY")
        print("This represents current standing based on completed work.")
        print("Ungraded assignments are excluded from calculation.")
        print("Use --include-ungraded to include all assignments.")
        print("=" * 70)

    # Print grade lists
    print_grade_list(processor, sort_by='name')
    print_grade_list(processor, sort_by='grade')

    # Determine output directory
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        # Create directory with format {course}-{date}
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        output_dir = Path(f"{course_code}-{today}")
    
    output_dir.mkdir(exist_ok=True)
    print(f"\nOutput directory: {output_dir}")

    print("\nGenerating reports...")
    save_csv_report(processor, str(output_dir / 'grades_summary.csv'))
    save_anomaly_report(processor, str(output_dir / 'anomaly_report.txt'))
    processor.save_individual_reports(str(output_dir / 'individual-grades'))

    print("\nDone!")


if __name__ == "__main__":
    main()
