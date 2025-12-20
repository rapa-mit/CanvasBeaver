# Registrar Upload CSV Feature

## Overview

The `process_grades.py` script now automatically generates a CSV file in the registrar's required format for grade submission.

## Output File

The file `registrar_upload.csv` is created in the output directory alongside other grade reports.

## Format

The CSV file contains the following columns as required by the registrar:

| Column | Description | Source |
|--------|-------------|--------|
| Last Name | Student's last name | Parsed from Canvas name field |
| First Name | Student's first name | Parsed from Canvas name field |
| Middle Name | Student's middle name | Empty (not available in Canvas) |
| MIT ID | Student's MIT ID number | Canvas SIS User ID (e.g., "123456789") |
| Subject # | Course number | Course code from Canvas (e.g., 16.001) |
| Section # | Section number | Empty (can be configured if needed) |
| Grade | Letter grade | Modified letter grade if specified, otherwise regular letter grade |
| Units | Course units | Empty (can be configured if needed) |
| Comment | Additional comments | Empty |

## Usage

The registrar CSV is automatically generated when running `process_grades.py`:

```bash
python3 process_grades.py --config grade_config_canvas.yaml --course-id 33045
```

The output will include:
```
Output directory: 16.001-2025-12-20

Generating reports...
Saved CSV summary to 16.001-2025-12-20/grades_summary.csv
Saved registrar upload file to 16.001-2025-12-20/registrar_upload.csv
Saved anomaly report to 16.001-2025-12-20/anomaly_report.txt
Saved 57 individual text and Excel reports to 16.001-2025-12-20/individual-grades/
```

## Modified Grades

When using the `--modified-grade-scale` option, the registrar upload will automatically use the modified letter grades:

```bash
python3 process_grades.py --config grade_config_canvas.yaml --course-id 33045 \
    --modified-grade-scale adjusted-letter-grades.yaml
```

This ensures that the grades submitted to the registrar match the modified grading scale.

## Example Output

```csv
Last Name,First Name,Middle Name,MIT ID,Subject #,Section #,Grade,Units,Comment
Smith,Alice,,123456789,16.001,,A-,,
Johnson,Bob,,234567890,16.001,,A,,
Williams,Carol,,345678901,16.001,,A+,,
```

## Customization

If you need to add values to the empty fields (Section #, Units, or Comment), you can modify the `save_registrar_report()` function in `process_grades.py`.

For example, to add a fixed unit value:
```python
row = {
    ...
    'Units': '12',  # Add fixed unit value
    ...
}
```

## Notes

- Students are sorted alphabetically by last name, then first name
- Names are automatically parsed from the Canvas "name" field
- If middle names are needed and available, you would need to obtain them from a separate data source
- The MIT ID field uses the Canvas SIS User ID, which contains the 9-digit MIT ID number
