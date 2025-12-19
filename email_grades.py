#!/usr/bin/env python3
"""
email_grades.py
--------------------------------
Email individual grade reports to students.

This script reads the processed grade data and individual grade report files,
then sends personalized emails to each student with their grade report attached.

Usage:
  python3 email_grades.py --course-id ID [options]

Requirements:
  - Individual grade files must exist in individual-grades/ directory
  - Students must have email addresses in Canvas
  - SMTP configuration (set in CONFIG section below)
"""
from __future__ import annotations

import argparse
import os
import smtplib
import pickle
import getpass
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import Optional
from datetime import datetime

from canvas.connection import CanvasConnection
from canvas.course import Course
from canvas.gradebook import get_course_gradebook


# ============================================================================
# EMAIL CONFIGURATION - Edit these values for your setup
# ============================================================================
# CONFIG = {
#     # Required: Your email address (sender)
#     'EMAIL_FROM': 'your.email@example.com',

#     # SMTP Server Settings
#     'SMTP_SERVER': 'smtp.example.com',  # e.g., smtp.gmail.com, outgoing.mit.edu
#     'SMTP_PORT': 587,                    # 587 for TLS, 25 for plain, 465 for SSL
#     'SMTP_USE_TLS': True,                # Use TLS encryption (recommended)

#     # SMTP Authentication (leave None if no auth required)
#     'SMTP_USER': None,                   # e.g., 'your.email@gmail.com'
#     'SMTP_PASSWORD': None,               # e.g., 'your-app-password'

#     # Email Subject
#     'EMAIL_SUBJECT': 'Your Course Grade Report',
# }

# Common configurations (uncomment and modify one):

# Gmail:
# CONFIG = {
#     'EMAIL_FROM': 'your.email@gmail.com',
#     'SMTP_SERVER': 'smtp.gmail.com',
#     'SMTP_PORT': 587,
#     'SMTP_USE_TLS': True,
#     'SMTP_USER': 'your.email@gmail.com',
#     'SMTP_PASSWORD': 'your-app-password',  # Use App Password, not regular password!
#     'EMAIL_SUBJECT': 'Your Course Grade Report',
# }

# MIT (with authentication - port 465 for SSL):
CONFIG = {
    'EMAIL_FROM': 'rapa@mit.edu',
    'SMTP_SERVER': 'outgoing.mit.edu',
    'SMTP_PORT': 465,  # Use 465 for SSL/TLS (not 587)
    'SMTP_USE_TLS': True,
    'SMTP_USER': 'rapa',  # Your MIT username
    'SMTP_PASSWORD': None,  # Leave None to prompt at runtime (more secure)
    'EMAIL_SUBJECT': 'Your Course Grade Report',
}

# Local SMTP (no auth):
# CONFIG = {
#     'EMAIL_FROM': 'professor@university.edu',
#     'SMTP_SERVER': 'localhost',
#     'SMTP_PORT': 25,
#     'SMTP_USE_TLS': False,
#     'SMTP_USER': None,
#     'SMTP_PASSWORD': None,
#     'EMAIL_SUBJECT': 'Your Course Grade Report',
# }
# ============================================================================


def send_email_with_attachment(
    to_email: str,
    from_email: str,
    subject: str,
    body: str,
    attachment_path: Optional[Path] = None,
    attachment_paths: Optional[list] = None,
    smtp_server: str = "localhost",
    smtp_port: int = 587,
    smtp_user: Optional[str] = None,
    smtp_password: Optional[str] = None,
    use_tls: bool = True,
    retry_on_auth_fail: bool = False,
) -> tuple:
    """Send an email with optional attachment(s).

    Args:
        to_email: Recipient email address
        from_email: Sender email address
        subject: Email subject line
        body: Email body text
        attachment_path: Optional path to single file to attach (for backward compatibility)
        attachment_paths: Optional list of paths to files to attach
        smtp_server: SMTP server hostname
        smtp_port: SMTP server port
        smtp_user: SMTP username (if authentication required)
        smtp_password: SMTP password (if authentication required)
        use_tls: Use TLS encryption
        retry_on_auth_fail: If True, returns special status on auth failure

    Returns:
        Tuple of (success: bool, error_type: Optional[str])
        error_type is 'auth_failed' if authentication failed, None otherwise
    """
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject

        # Add body
        msg.attach(MIMEText(body, 'plain'))

        # Collect all attachments
        attachments = []
        if attachment_path and attachment_path.exists():
            attachments.append(attachment_path)
        if attachment_paths:
            attachments.extend([p for p in attachment_paths if p.exists()])

        # Add all attachments
        for attach_path in attachments:
            with open(attach_path, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())

            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename={attach_path.name}'
            )
            msg.attach(part)

        # Connect to SMTP server and send
        # Port 465 uses implicit SSL (SMTP_SSL), others use STARTTLS
        if smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        elif use_tls:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
        else:
            server = smtplib.SMTP(smtp_server, smtp_port)

        if smtp_user and smtp_password:
            server.login(smtp_user, smtp_password)

        server.send_message(msg)
        server.quit()

        return (True, None)

    except smtplib.SMTPAuthenticationError as e:
        if retry_on_auth_fail:
            print(f"  ERROR: SMTP authentication failed")
            return (False, 'auth_failed')
        else:
            print(f"  ERROR: SMTP authentication failed: {e}")
            print(f"  Check your SMTP_USER and SMTP_PASSWORD settings.")
            return (False, None)
    except smtplib.SMTPRecipientsRefused as e:
        print(f"  ERROR: Recipient refused: {e}")
        print(f"  The SMTP server rejected the recipient address.")
        return (False, None)
    except smtplib.SMTPSenderRefused as e:
        print(f"  ERROR: Sender refused: {e}")
        print(f"  The SMTP server rejected the sender address (from: {from_email}).")
        return (False, None)
    except Exception as e:
        print(f"  ERROR: Failed to send email to {to_email}: {e}")
        return (False, None)


def get_email_config(prompt_password: bool = False) -> dict:
    """Get email configuration from CONFIG constant (with env var fallback).
    
    Args:
        prompt_password: If True, prompt for password if not set
    """
    config = {
        'smtp_server': os.environ.get('SMTP_SERVER', CONFIG['SMTP_SERVER']),
        'smtp_port': int(os.environ.get('SMTP_PORT', str(CONFIG['SMTP_PORT']))),
        'smtp_user': os.environ.get('SMTP_USER', CONFIG['SMTP_USER']),
        'smtp_password': os.environ.get('SMTP_PASSWORD', CONFIG['SMTP_PASSWORD']),
        'use_tls': os.environ.get('SMTP_USE_TLS', str(CONFIG['SMTP_USE_TLS'])).lower() in ('true', '1', 'yes'),
        'from_email': os.environ.get('EMAIL_FROM', CONFIG['EMAIL_FROM']),
    }
    
    # Prompt for password if needed and requested
    if prompt_password and config['smtp_user'] and not config['smtp_password']:
        # Try to load from cache first
        cached_password = load_cached_password(config['smtp_user'], config['smtp_server'])
        if cached_password:
            print(f"\nUsing cached password for {config['smtp_user']}@{config['smtp_server']}")
            config['smtp_password'] = cached_password
        else:
            print(f"\nSMTP Authentication required for {config['smtp_user']}@{config['smtp_server']}")
            config['smtp_password'] = getpass.getpass(f"Enter password for {config['smtp_user']}: ")
    
    return config


def sanitize_filename(name: str) -> str:
    """Convert student name to filename (matching process_grades.py convention)."""
    return name


def get_password_cache_file() -> Path:
    """Get the path to the password cache file."""
    return Path.home() / '.canvas_email_password.pkl'


def load_cached_password(smtp_user: str, smtp_server: str) -> Optional[str]:
    """Load cached password for given user/server if available.
    
    Args:
        smtp_user: SMTP username
        smtp_server: SMTP server
        
    Returns:
        Cached password or None if not found
    """
    cache_file = get_password_cache_file()
    if not cache_file.exists():
        return None
    
    try:
        with open(cache_file, 'rb') as f:
            cache = pickle.load(f)
        key = f"{smtp_user}@{smtp_server}"
        return cache.get(key)
    except Exception:
        return None


def save_password_to_cache(smtp_user: str, smtp_server: str, password: str) -> None:
    """Save password to cache file.
    
    Args:
        smtp_user: SMTP username
        smtp_server: SMTP server
        password: Password to cache
    """
    cache_file = get_password_cache_file()
    
    # Load existing cache
    cache = {}
    if cache_file.exists():
        try:
            with open(cache_file, 'rb') as f:
                cache = pickle.load(f)
        except Exception:
            cache = {}
    
    # Update cache
    key = f"{smtp_user}@{smtp_server}"
    cache[key] = password
    
    # Save cache with restricted permissions
    try:
        with open(cache_file, 'wb') as f:
            pickle.dump(cache, f)
        # Set file permissions to user-only read/write (0600)
        cache_file.chmod(0o600)
    except Exception as e:
        print(f"Warning: Could not save password cache: {e}")


def clear_password_cache() -> None:
    """Clear the password cache file."""
    cache_file = get_password_cache_file()
    if cache_file.exists():
        cache_file.unlink()


def test_email_configuration(email_config: dict, retry_password: bool = True) -> bool:
    """Test email configuration by sending a test message.
    
    Args:
        email_config: Email configuration dictionary
        retry_password: If True, ask for password again on auth failure
        
    Returns:
        True if test email sent successfully, False otherwise
    """
    print("\n" + "="*70)
    print("TESTING EMAIL CONFIGURATION")
    print("="*70)
    print(f"From: {email_config['from_email']}")
    print(f"SMTP Server: {email_config['smtp_server']}:{email_config['smtp_port']}")
    print(f"TLS: {email_config['use_tls']}")
    print(f"Authentication: {'Yes' if email_config['smtp_user'] else 'No'}")
    
    # Check for common configuration issues
    if 'mit.edu' in email_config['smtp_server']:
        if not email_config['smtp_user'] or not email_config['smtp_password']:
            print("\nNOTE: MIT SMTP requires authentication.")
            print("  Set SMTP_USER (your MIT username) and SMTP_PASSWORD")
            print("  Use port 465 with SSL/TLS for authenticated access.")
        elif email_config['smtp_port'] != 465:
            print("\nNOTE: For MIT SMTP with authentication, use port 465 (not 587).")
    
    print()
    
    test_recipient = input("Enter email address to send test to (or press Enter to skip): ").strip()
    
    if not test_recipient:
        print("Skipping email test.")
        return True
    
    print(f"\nSending test email to {test_recipient}...")
    
    test_subject = "Canvas Grade Email System - Test Message"
    test_body = f"""This is a test message from the Canvas grade email system.

Configuration:
- From: {email_config['from_email']}
- SMTP Server: {email_config['smtp_server']}:{email_config['smtp_port']}
- TLS Enabled: {email_config['use_tls']}
- Authentication: {'Yes' if email_config['smtp_user'] else 'No'}

If you received this message, your email configuration is working correctly!

This was sent at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    try:
        success, error_type = send_email_with_attachment(
            to_email=test_recipient,
            from_email=email_config['from_email'],
            subject=test_subject,
            body=test_body,
            attachment_path=None,
            smtp_server=email_config['smtp_server'],
            smtp_port=email_config['smtp_port'],
            smtp_user=email_config['smtp_user'],
            smtp_password=email_config['smtp_password'],
            use_tls=email_config['use_tls'],
            retry_on_auth_fail=retry_password,
        )
        
        if success:
            print("✓ Test email sent successfully!")
            print(f"  Check {test_recipient} for the test message.")
            # Save password to cache on success
            if email_config['smtp_user'] and email_config['smtp_password']:
                save_password_to_cache(
                    email_config['smtp_user'],
                    email_config['smtp_server'],
                    email_config['smtp_password']
                )
            return True
        elif error_type == 'auth_failed' and retry_password:
            print("  Password may be incorrect or cached password expired.")
            # Clear the bad password from cache
            if email_config['smtp_user']:
                cache_file = get_password_cache_file()
                if cache_file.exists():
                    try:
                        with open(cache_file, 'rb') as f:
                            cache = pickle.load(f)
                        key = f"{email_config['smtp_user']}@{email_config['smtp_server']}"
                        if key in cache:
                            del cache[key]
                            with open(cache_file, 'wb') as f:
                                pickle.dump(cache, f)
                            cache_file.chmod(0o600)
                    except Exception:
                        pass
            
            # Ask for password again
            print("\nPlease enter your password again:")
            email_config['smtp_password'] = getpass.getpass(f"Enter password for {email_config['smtp_user']}: ")
            
            # Retry with new password (but don't retry again to avoid loop)
            return test_email_configuration(email_config, retry_password=False)
        else:
            print("✗ Failed to send test email.")
            return False
            
    except Exception as e:
        print(f"✗ Error testing email configuration: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Email individual grade reports to students")
    parser.add_argument("--course-id", type=int, help="Canvas course ID (optional)")
    parser.add_argument("--reports-dir", type=str,
                       help="Directory containing individual grade report files (default: {course}-{date}/individual-grades)")
    parser.add_argument("--subject", type=str,
                       default=CONFIG.get('EMAIL_SUBJECT', 'Your Course Grade Report'),
                       help="Email subject line")
    parser.add_argument("--from-email", type=str, help="Sender email address")
    parser.add_argument("--smtp-server", type=str, help="SMTP server hostname")
    parser.add_argument("--smtp-port", type=int, help="SMTP server port")
    parser.add_argument("--smtp-user", type=str, help="SMTP username")
    parser.add_argument("--smtp-password", type=str, help="SMTP password")
    parser.add_argument("--no-tls", action="store_true", help="Disable TLS encryption")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be sent without actually sending")
    parser.add_argument("--test-email", type=str,
                       help="Send all emails to this test address instead of students")
    parser.add_argument("--no-cache", action="store_true",
                       help="Skip cache, always download fresh from Canvas")
    parser.add_argument("--test-config", action="store_true",
                       help="Test email configuration and exit")
    parser.add_argument("--no-confirm", action="store_true",
                       help="Don't ask for confirmation before each email")
    parser.add_argument("--final-grades", action="store_true",
                       help="Use final grades message (instead of mid-semester message)")
    args = parser.parse_args()

    # Load email configuration (CONFIG constant + env vars + command line overrides)
    # Don't prompt for password yet - wait until we need it
    email_config = get_email_config(prompt_password=False)

    if args.from_email:
        email_config['from_email'] = args.from_email
    if args.smtp_server:
        email_config['smtp_server'] = args.smtp_server
    if args.smtp_port:
        email_config['smtp_port'] = args.smtp_port
    if args.smtp_user:
        email_config['smtp_user'] = args.smtp_user
    if args.smtp_password:
        email_config['smtp_password'] = args.smtp_password
    if args.no_tls:
        email_config['use_tls'] = False

    # Validate required config
    if not email_config['from_email']:
        print("ERROR: Sender email address required (set in CONFIG or use --from-email)")
        return 1

    # If just testing configuration, do that and exit
    if args.test_config:
        # Prompt for password if needed
        if email_config['smtp_user'] and not email_config['smtp_password']:
            # Try cached password first
            cached_password = load_cached_password(email_config['smtp_user'], email_config['smtp_server'])
            if cached_password:
                print(f"\nUsing cached password for {email_config['smtp_user']}@{email_config['smtp_server']}")
                email_config['smtp_password'] = cached_password
            else:
                print(f"\nSMTP Authentication required for {email_config['smtp_user']}@{email_config['smtp_server']}")
                email_config['smtp_password'] = getpass.getpass(f"Enter password for {email_config['smtp_user']}: ")
        success = test_email_configuration(email_config)
        return 0 if success else 1

    # Connect to Canvas
    print("Connecting to Canvas...")
    conn = CanvasConnection()
    course = Course.from_args(conn, args.course_id)
    course_id = course.course_id
    course_code = course.course_code

    # Find latest cache file for this course
    import glob
    cache_pattern = f"gradebook_{course_id}_*.pkl"
    cache_files = sorted(glob.glob(cache_pattern), reverse=True)

    use_cache = False
    if cache_files and not args.no_cache:
        latest_cache = cache_files[0]
        cache_time = os.path.getmtime(latest_cache)
        cache_date = datetime.fromtimestamp(cache_time).strftime("%Y-%m-%d %H:%M:%S")

        print(f"\nFound cached gradebook: {latest_cache}")
        print(f"  Downloaded: {cache_date}")
        response = input("Use cached data? (Y/n): ").strip().lower()
        use_cache = response != 'n'

    # Load gradebook
    if use_cache:
        print(f"Loading gradebook from cache: {latest_cache}")
        from canvas.gradebook import Gradebook
        gb = Gradebook.load_from_cache(latest_cache)
    else:
        print(f"Loading gradebook for: {course.name}")
        gb = get_course_gradebook(conn, course_id, include_inactive=False)

        # Save to cache
        today = datetime.now().strftime("%Y%m%d")
        cache_file = f"gradebook_{course_id}_{today}.pkl"
        gb.save_to_cache(cache_file)

    students = gb.get_students()
    
    # Determine reports directory
    if args.reports_dir:
        reports_dir = Path(args.reports_dir)
    else:
        # Default: look in {course}-{date}/individual-grades
        today = datetime.now().strftime("%Y-%m-%d")
        reports_dir = Path(f"{course_code}-{today}") / "individual-grades"

    if not reports_dir.exists():
        print(f"ERROR: Reports directory not found: {reports_dir}")
        print("Please run process_grades.py first to generate individual reports.")
        return 1

    print(f"\nFound {len(students)} students")
    print(f"Reports directory: {reports_dir}")
    print(f"Email configuration:")
    print(f"  From: {email_config['from_email']}")
    print(f"  SMTP: {email_config['smtp_server']}:{email_config['smtp_port']}")
    print(f"  TLS: {email_config['use_tls']}")
    print(f"  Auth: {'Yes' if email_config['smtp_user'] else 'No'}")

    if args.dry_run:
        print("\n*** DRY RUN MODE - No emails will be sent ***\n")

    if args.test_email:
        print(f"\n*** TEST MODE - All emails will be sent to {args.test_email} ***\n")

    # Prompt for password if needed (before we start sending)
    if not args.dry_run:
        if email_config['smtp_user'] and not email_config['smtp_password']:
            # Try cached password first
            cached_password = load_cached_password(email_config['smtp_user'], email_config['smtp_server'])
            if cached_password:
                print(f"\nUsing cached password for {email_config['smtp_user']}@{email_config['smtp_server']}")
                email_config['smtp_password'] = cached_password
            else:
                print(f"\nSMTP Authentication required for {email_config['smtp_user']}@{email_config['smtp_server']}")
                email_config['smtp_password'] = getpass.getpass(f"Enter password for {email_config['smtp_user']}: ")
    
    # Offer to test email configuration first
    if not args.dry_run and not args.test_email:
        response = input("\nTest email configuration before sending? (y/N): ").strip().lower()
        if response in ('y', 'yes'):
            test_success = test_email_configuration(email_config)
            if not test_success:
                print("\nEmail test failed. Please fix configuration before continuing.")
                response = input("Continue anyway? (yes/no): ").strip().lower()
                if response not in ('yes', 'y'):
                    print("Cancelled.")
                    return 0

    # Confirm before sending
    if not args.dry_run:
        response = input("\nProceed with sending emails? (yes/no): ").strip().lower()
        if response not in ('yes', 'y'):
            print("Cancelled.")
            return 0

    # Email each student
    sent_count = 0
    failed_count = 0
    skipped_count = 0
    user_quit = False

    for idx, student in enumerate(students, 1):
        if user_quit:
            print(f"SKIP: {student.name} - user cancelled")
            skipped_count += 1
            continue
            
        if not student.email:
            print(f"SKIP: {student.name} - no email address")
            skipped_count += 1
            continue

        # Find grade report files (text and Excel)
        report_file = reports_dir / f"{sanitize_filename(student.name)}.txt"
        excel_file = reports_dir / f"{sanitize_filename(student.name)}.xlsx"

        if not report_file.exists():
            print(f"SKIP: {student.name} - no report file found ({report_file.name})")
            skipped_count += 1
            continue

        # Prepare email
        to_email = args.test_email if args.test_email else student.email

        # Read the grade report file content
        with open(report_file, 'r', encoding='utf-8') as f:
            report_content = f.read()

        # Check if Excel file exists
        has_excel = excel_file.exists()

        # Build email body based on whether these are final grades or mid-semester
        if args.final_grades:
            # Final grades message
            body = f"""Dear {student.name},

Here is your final grade report for {course.name}.

This report shows your final course grade based on all graded assignments completed this semester.

"""
            if has_excel:
                body += f"""I've attached an Excel spreadsheet with your grades. The spreadsheet includes:
- All your assignment scores organized by category
- Formulas showing exactly how your grade is calculated
- A "Grades" sheet with the letter grade conversion scale
- Complete breakdown of all work completed during the semester

"""

            body += f"""These are your official final grades for the course. If you have any questions about your final grade calculation, please don't hesitate to reach out.

Thank you for your hard work this semester!

Best regards

{'='*70}

{report_content}
"""
        else:
            # Mid-semester / progress report message
            body = f"""Dear {student.name},

Here is your individual grade report for {course.name}.

This report shows your current standing based on graded assignments completed so far this semester.

"""

            if has_excel:
                body += f"""I've attached an Excel spreadsheet with your grades. The spreadsheet includes:
- All your assignment scores organized by category
- Formulas showing exactly how your grade is calculated
- A "Grades" sheet with the letter grade conversion scale
- You can modify scores to see how hypothetical changes would affect your grade

"""

            body += f"""If you have any questions about your grades, please don't hesitate to reach out.

Best regards

────────────────────────
IMPORTANT DISCLAIMER:

I want to clarify once again that this is just for the purpose of giving you an idea of how to compute your grade based on the work done so far. The percentage and the letter grade is not a predictor of your final course grade, as it's missing a large part of the grade (final %35%, and several ungraded or unassigned psets, labs and quizlets). The computation of your current grade is done by normalizing the scores you have obtained with the maximum score possible in all the work graded so far.
────────────────────────

{'='*70}

{report_content}
"""

        # Ask for confirmation before sending (unless --no-confirm flag is set)
        if not args.dry_run and not args.no_confirm:
            print(f"\n{'='*70}")
            print(f"Student {idx}/{len(students)}: {student.name}")
            print(f"{'='*70}")
            print(f"Email: {to_email}")
            print(f"Report file: {report_file.name}")
            if has_excel:
                print(f"Excel file: {excel_file.name}")
            else:
                print(f"Excel file: (not found)")
            print()
            
            while True:
                response = input("Send email? ([y]es/[n]o/[q]uit/[p]review/[a]ll): ").strip().lower()
                
                if response in ('y', 'yes', ''):
                    # Send this email
                    break
                elif response in ('n', 'no', 's', 'skip'):
                    # Skip this student
                    print(f"SKIP: {student.name}")
                    skipped_count += 1
                    break
                elif response in ('q', 'quit', 'exit'):
                    # Quit - skip remaining students
                    print("Quitting. Remaining students will be skipped.")
                    user_quit = True
                    skipped_count += 1
                    break
                elif response in ('p', 'preview'):
                    # Show email preview
                    print(f"\n{'-'*70}")
                    print(f"EMAIL PREVIEW")
                    print(f"{'-'*70}")
                    print(f"To: {to_email}")
                    print(f"From: {email_config['from_email']}")
                    print(f"Subject: {args.subject}")
                    print(f"\n{body[:500]}...")
                    print(f"{'-'*70}\n")
                    continue
                elif response in ('a', 'all'):
                    # Send this and all remaining without asking
                    print("Sending to all remaining students without confirmation...")
                    args.no_confirm = True
                    break
                else:
                    print("Invalid choice. Please enter 'y', 'n', 'q', 'p', or 'a'")
                    continue
            
            # If user chose to skip or quit, continue to next student
            if response in ('n', 'no', 's', 'skip') or user_quit:
                continue
        
        # Send or simulate
        if args.dry_run:
            print(f"WOULD SEND: {student.name} <{to_email}>")
            print(f"  Report inlined in email body")
            if has_excel:
                print(f"  Excel attachment: {excel_file.name}")
            sent_count += 1
        else:
            if args.no_confirm:
                print(f"Sending to {student.name} <{to_email}>...", end=" ")
            else:
                print(f"Sending...", end=" ")
            success, _ = send_email_with_attachment(
                to_email=to_email,
                from_email=email_config['from_email'],
                subject=args.subject,
                body=body,
                attachment_path=excel_file if has_excel else None,
                smtp_server=email_config['smtp_server'],
                smtp_port=email_config['smtp_port'],
                smtp_user=email_config['smtp_user'],
                smtp_password=email_config['smtp_password'],
                use_tls=email_config['use_tls'],
            )

            if success:
                print("✓ Sent")
                sent_count += 1
                # Save password to cache on first successful send
                if email_config['smtp_user'] and email_config['smtp_password'] and sent_count == 1:
                    save_password_to_cache(
                        email_config['smtp_user'],
                        email_config['smtp_server'],
                        email_config['smtp_password']
                    )
            else:
                failed_count += 1

    # Summary
    print(f"\n{'='*70}")
    print("EMAIL SUMMARY")
    print(f"{'='*70}")
    print(f"Successfully sent: {sent_count}")
    print(f"Failed: {failed_count}")
    print(f"Skipped (no email/report): {skipped_count}")
    print(f"Total students: {len(students)}")

    if args.dry_run:
        print("\n(This was a dry run - no emails were actually sent)")

    return 0 if failed_count == 0 else 1


if __name__ == "__main__":
    exit(main())
