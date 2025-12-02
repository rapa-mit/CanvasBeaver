#!/usr/bin/env python3
"""
generate_config.py
--------------------------------
Generate grade configuration YAML file from Canvas assignment groups.

This script scans your Canvas course and creates a configuration file
with all assignment groups detected. You can then customize drop_lowest
rules as needed.

Usage:
  python3 generate_config.py [--course-id ID] [--output FILE] [--interactive]
  
Options:
  --course-id ID       Canvas course ID (interactive if not specified)
  --output FILE        Output YAML file (default: grade_config_{course}.yaml)
  --interactive        Prompt for drop_lowest values interactively
  --force              Overwrite existing config file
"""
from __future__ import annotations

import argparse
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

from canvas.connection import CanvasConnection
from canvas.course import Course


def generate_config_from_canvas(
    course_id: int,
    canvas_connection: CanvasConnection,
    interactive: bool = False
) -> Dict[str, Any]:
    """Generate configuration by scanning Canvas assignment groups.
    
    Args:
        course_id: Canvas course ID
        canvas_connection: Active Canvas connection
        interactive: If True, prompt user for drop_lowest values
        
    Returns:
        Dictionary containing configuration
    """
    canvas = canvas_connection.get_canvas()
    canvas_course = canvas.get_course(course_id)
    
    # Get assignment groups
    assignment_groups = list(canvas_course.get_assignment_groups())
    
    # Check if course uses weighted groups
    uses_weights = getattr(canvas_course, 'apply_assignment_group_weights', False)
    
    print(f"\nFound {len(assignment_groups)} assignment groups:")
    print("=" * 70)
    
    drop_lowest = {}
    
    for g in assignment_groups:
        weight = getattr(g, 'group_weight', 0)
        rules = getattr(g, 'rules', {})
        
        print(f"\n{g.name}:")
        print(f"  Weight: {weight}%")
        print(f"  Position: {getattr(g, 'position', 'N/A')}")
        
        # Check if Canvas has drop rules configured
        canvas_drop = rules.get('drop_lowest', 0) if rules else 0
        if canvas_drop > 0:
            print(f"  Canvas drop_lowest: {canvas_drop}")
            drop_lowest[g.name] = canvas_drop
        
        if interactive:
            # Prompt user for drop_lowest value
            default = canvas_drop if canvas_drop > 0 else 0
            prompt = f"  Drop lowest assignments for '{g.name}'? [{default}]: "
            response = input(prompt).strip()
            
            if response:
                try:
                    drop_val = int(response)
                    if drop_val > 0:
                        drop_lowest[g.name] = drop_val
                except ValueError:
                    print(f"    Invalid number, using {default}")
                    if default > 0:
                        drop_lowest[g.name] = default
            elif default > 0:
                drop_lowest[g.name] = default
    
    print("\n" + "=" * 70)
    
    if not uses_weights:
        print("\n⚠ WARNING: Course does not have 'Weighted by Group' enabled!")
        print("  Go to Canvas → Settings → Enable 'Weighted by Group'")
    
    # Build configuration
    config = {
        'use_canvas_groups': True,
        'drop_lowest': drop_lowest if drop_lowest else {},
    }
    
    # Add comments
    return config


def save_config_with_comments(config: Dict[str, Any], output_file: str) -> None:
    """Save configuration with helpful comments."""
    
    with open(output_file, 'w') as f:
        f.write("# Grade Processing Configuration\n")
        f.write("# " + "=" * 68 + "\n")
        f.write("# Auto-generated configuration using Canvas assignment groups\n")
        f.write("#\n")
        f.write("# This configuration pulls assignment groups and weights from Canvas.\n")
        f.write("# You can edit the drop_lowest values below as needed.\n")
        f.write("\n")
        
        f.write("# Use Canvas Assignment Groups\n")
        f.write("# -----------------------------\n")
        f.write(f"use_canvas_groups: {config['use_canvas_groups']}\n")
        f.write("\n")
        
        f.write("# Drop Lowest Grades\n")
        f.write("# ------------------\n")
        f.write("# Number of lowest grades to drop for each assignment group\n")
        f.write("# Use the exact assignment group names from Canvas\n")
        
        if config['drop_lowest']:
            f.write("drop_lowest:\n")
            for group_name, count in config['drop_lowest'].items():
                f.write(f"  {group_name}: {count}\n")
        else:
            f.write("# drop_lowest:\n")
            f.write("#   Problem Sets: 1    # Example: drop lowest problem set\n")
            f.write("#   Quizzes: 1         # Example: drop lowest quiz\n")
        
        f.write("\n")
        f.write("# Letter Grade Scale (Optional)\n")
        f.write("# ------------------------------\n")
        f.write("# Path to custom letter grade scale YAML file\n")
        f.write("# If not specified, uses MIT-letter-grades.yaml by default\n")
        f.write("# letter_grade_scale: MIT-letter-grades.yaml\n")
        f.write("# letter_grade_scale: strict-letter-grades.yaml\n")
        f.write("\n")
        f.write("# Notes:\n")
        f.write("# ------\n")
        f.write("# - Grade weights are automatically fetched from Canvas\n")
        f.write("# - Make sure 'Weighted by Group' is enabled in Canvas\n")
        f.write("# - Assignment group names must exactly match Canvas\n")


def main():
    parser = argparse.ArgumentParser(
        description="Generate grade configuration from Canvas assignment groups"
    )
    parser.add_argument("--course-id", type=int, help="Canvas course ID (optional)")
    parser.add_argument("--output", type=str, help="Output YAML file")
    parser.add_argument("--interactive", action="store_true",
                       help="Prompt for drop_lowest values interactively")
    parser.add_argument("--force", action="store_true",
                       help="Overwrite existing config file")
    args = parser.parse_args()
    
    print("Grade Configuration Generator")
    print("=" * 70)
    
    # Connect to Canvas
    print("\nConnecting to Canvas...")
    conn = CanvasConnection()
    course = Course.from_args(conn, args.course_id)
    
    print(f"Course: {course.name}")
    print(f"Course ID: {course.course_id}")
    print(f"Course code: {course.course_code}")
    
    # Determine output filename
    if args.output:
        output_file = args.output
    else:
        # Default: grade_config_{course_code}.yaml
        safe_code = course.course_code.replace('/', '-').replace(' ', '_')
        output_file = f"grade_config_{safe_code}.yaml"
    
    # Check if file exists
    if Path(output_file).exists() and not args.force:
        print(f"\n⚠ Config file already exists: {output_file}")
        response = input("Overwrite? (y/N): ").strip().lower()
        if response != 'y':
            print("Cancelled.")
            return 1
    
    # Generate configuration
    config = generate_config_from_canvas(
        course.course_id,
        conn,
        interactive=args.interactive
    )
    
    # Save configuration
    save_config_with_comments(config, output_file)
    
    print(f"\n✓ Configuration saved to: {output_file}")
    print(f"\nYou can now use it with:")
    print(f"  python3 process_grades.py --config {output_file}")
    
    if not args.interactive and not config['drop_lowest']:
        print(f"\nTip: Run with --interactive to set drop_lowest values:")
        print(f"  python3 generate_config.py --interactive")


if __name__ == "__main__":
    main()
