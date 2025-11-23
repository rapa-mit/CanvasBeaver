# Simplified Grade Calculation

## The Simple Approach

**Goal:** If the graded work so far = 100%, what percentage did the student earn?

## Calculation Steps

### Step 1: Average graded assignments in each category
For each category (Problem Sets, Quizlets, Midterm, Final):
- Take all graded assignments
- Apply drop_lowest if configured
- Calculate average percentage

### Step 2: Calculate weighted contributions
For each category with graded work:
```
contribution = average_percentage × category_weight
```

Example:
- Problem Sets: 97.69% × 15% = 14.65%
- Quizlets: 102.38% × 25% = 25.60%
- Midterm: 102.72% × 25% = 25.68%
- **Sum: 65.93%**

### Step 3: Normalize to 100%
```
total_weight_of_graded_categories = sum of weights where work is graded
current_grade = sum_of_contributions / total_weight_of_graded_categories
```

Example:
- Graded categories: PS (15%) + Quiz (25%) + Mid (25%) = 65%
- Current grade: 65.93% / 0.65 = **101.43%**

## That's It!

No complex calculations about proportions of assignments within categories.
Simple logic: 
1. Average what's graded in each category
2. Weight by category weight
3. Normalize by total weight of graded categories

## Report Display

```
CURRENT GRADE (on graded work): 101.43% = A+
(Graded categories worth 65% of course, normalized to 100%)

PROBLEM SETS
------------
  Problem Set #1                                100.00%  (5.00 pts)
  Problem Set #2                                100.00%  (5.00 pts)
  ...
  
  Average across 8 assignment(s): 97.69%
  Weighted contribution: 14.65%
  As % of graded work: 22.54%

QUIZLETS
--------
  ...
  
  Average across 6 assignment(s): 102.38%
  Weighted contribution: 25.60%
  As % of graded work: 39.39%

MIDTERM
-------
  16.001 Midterm                                102.72%  (94.50 pts)
  
  Average across 1 assignment(s): 102.72%
  Weighted contribution: 25.68%
  As % of graded work: 39.51%
```

## Key Points

- **Weighted contribution**: Shows actual points earned (avg × category weight)
- **As % of graded work**: Shows what this represents when normalized to 100%
- **No proportional scaling**: We don't reduce category weight based on how many assignments within that category are graded
- **Simple and transparent**: Easy to understand and verify

## Comparison to Old Complex Logic

**OLD (Complex):**
- Calculate proportion of assignments graded in each category
- Scale category weight by proportion (e.g., 15% × 8/16 = 7.5%)
- Use scaled weights for calculation
- Normalize by sum of scaled weights

**NEW (Simple):**
- Use full category weight (15%, 25%, 25%, 35%)
- If category has ANY graded work, include it with full weight
- Normalize by sum of included category weights

**Result:** Same normalized grade, much simpler logic!
