# Canvas Beaver - Gradebook Caching

## Overview

Canvas Beaver automatically caches gradebook data to speed up repeated runs. No more waiting for Canvas API downloads every time!

## How It Works

### Automatic Cache Management

1. **First run**: Downloads from Canvas, automatically saves cache
2. **Subsequent runs**: Detects cache, shows when it was downloaded, asks if you want to use it
3. **Smart naming**: Files named `gradebook_<course_id>_<date>.pkl`

### Cache File Format

Files are named: `gradebook_<course_id>_YYYYMMDD.pkl`

Examples:
- `gradebook_33045_20241123.pkl` - Course 33045, Nov 23, 2024
- `gradebook_33045_20241124.pkl` - Course 33045, Nov 24, 2024

The date reflects when the data was **downloaded**, not when you run the script.

## Usage

### Normal Usage (with cache)

```bash
python3 process_grades.py --config grade_config_canvas.yaml
```

**First time:**
```
Connecting to Canvas...
Loading gradebook for: Unified Engineering
Loaded 56 students, 28 assignments
Gradebook cached to gradebook_33045_20241123.pkl
```

**Second time (same day):**
```
Connecting to Canvas...

Found cached gradebook: gradebook_33045_20241123.pkl
  Downloaded: 2024-11-23 09:30:45
Use cached data? (Y/n): y

Loading gradebook from cache: gradebook_33045_20241123.pkl
  Course ID: 33045
  28 assignments, 56 students
```

Just press Enter (or type 'y') to use cached data.

### Force Fresh Download

If grades have been updated in Canvas and you want fresh data:

```bash
python3 process_grades.py --config grade_config_canvas.yaml --no-cache
```

This will:
- Skip the cache prompt
- Download fresh data from Canvas
- Save new cache with today's date

### Responding to the Prompt

When asked "Use cached data? (Y/n)":
- Press **Enter** or type **y** → Use cached data (fast!)
- Type **n** → Download fresh from Canvas (slower, but up-to-date)

## Benefits

### Speed
- **With cache**: Instant loading (< 1 second)
- **Without cache**: 30-60 seconds downloading from Canvas

### Convenience
- Automatic - no manual file management
- Smart prompts - shows when cache was created
- Easy override - just use `--no-cache`

### Historical Data
- Keep old cache files to compare grades over time
- Each day gets its own cache file
- Can see how grades evolved

## File Management

### Location
Cache files are saved in the current directory where you run the script.

### Cleanup
Old cache files can be safely deleted:

```bash
# Delete all cache files for course 33045
rm gradebook_33045_*.pkl

# Delete cache files older than 7 days
find . -name "gradebook_*.pkl" -mtime +7 -delete

# Keep only the latest cache
ls -t gradebook_33045_*.pkl | tail -n +2 | xargs rm
```

### .gitignore
Cache files are automatically excluded from git (see `.gitignore`).

## Technical Details

### Cache Format
Uses Python's `pickle` format for fast serialization:
- Very fast (instant load/save)
- Compact file size
- Handles all Python objects
- Binary format (not human-readable)

### What's Cached
The cache includes:
- All assignments (with IDs, names, points, due dates, groups)
- All students (with IDs, names, emails, login IDs)
- All scores (with points, percentages, submission info)
- Excused/late/missing flags

Everything needed for grade processing!

### What's NOT Cached
- Canvas API connection
- Grade processor settings (always from config file)
- Letter grade scale (always from YAML file)
- Drop lowest configuration (always from config file)

This means you can change config settings and use cached gradebook data.

## Example Workflow

### Daily Grade Processing

**Monday morning** (download fresh):
```bash
python3 process_grades.py --config grade_config_canvas.yaml --no-cache
```

**Monday afternoon** (rerun with different config):
```bash
# Edit grade_config_canvas.yaml to change drop_lowest
python3 process_grades.py --config grade_config_canvas.yaml
# Press Enter to use cached data (much faster!)
```

**Tuesday** (after grading more assignments):
```bash
python3 process_grades.py --config grade_config_canvas.yaml --no-cache
```

### Multiple Runs for Testing

```bash
# Download once
python3 process_grades.py --config grade_config_canvas.yaml --no-cache

# Test different letter grade scales (uses cache)
python3 process_grades.py --config grade_config_canvas.yaml
# Press Enter to use cache

# Edit MIT-letter-grades.yaml, run again (uses cache)
python3 process_grades.py --config grade_config_canvas.yaml
# Press Enter to use cache
```

## Troubleshooting

### "Found cached gradebook" but I want fresh data
Just type 'n' when prompted, or use `--no-cache` flag.

### Cache file is corrupted
Delete it and download fresh:
```bash
rm gradebook_*.pkl
python3 process_grades.py --config grade_config_canvas.yaml
```

### Want to disable caching entirely
Always use `--no-cache` flag:
```bash
python3 process_grades.py --config grade_config_canvas.yaml --no-cache
```

### Cache shows wrong course
The script detects cache files based on course ID. If you change courses, it will automatically create a new cache file for the new course.

## Performance Comparison

### Without Cache (every run)
```
Connecting to Canvas...        [2 sec]
Loading assignments...          [10 sec]
Loading students...             [5 sec]
Loading submissions...          [30 sec]
Processing grades...            [5 sec]
Total: ~52 seconds
```

### With Cache (subsequent runs)
```
Connecting to Canvas...        [2 sec]
Found cache, load?             [1 sec]
Loading from cache...          [0.5 sec]
Processing grades...           [5 sec]
Total: ~8.5 seconds
```

**Savings: ~45 seconds per run!**

## Best Practices

1. **Start of day**: Use `--no-cache` to get fresh data
2. **Multiple runs**: Accept cached data for speed
3. **After grading**: Use `--no-cache` to see updated scores
4. **Config changes**: Cached data works fine with different configs
5. **Weekly cleanup**: Delete old cache files to save disk space

## Summary

The caching feature makes grade processing much faster for repeated runs while staying simple and automatic. Just run the script normally and accept the cache when offered!
