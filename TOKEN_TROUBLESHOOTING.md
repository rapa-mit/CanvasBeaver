# Canvas API Token Troubleshooting

## Symptom: Can Create Assignments but Cannot Upload Grades

If you can successfully create assignments but get permission errors when trying to upload grades, your Canvas API token likely has **limited scope**.

## Understanding Canvas Token Scopes

Canvas allows API tokens to be created with restricted permissions. When generating a token, you can:
- Set an expiration date
- Limit the token's scope to specific API endpoints

**Problem**: If you created a token with limited scope, it might allow some operations (like creating assignments) but not others (like modifying grades).

## Solution: Regenerate Your API Token

### Step 1: Delete Old Token (Optional)

1. Log into Canvas
2. Click on **Account** (top-left) → **Settings**
3. Scroll down to **Approved Integrations**
4. Find your old token and click **Delete**

### Step 2: Generate New Token

1. In the same **Approved Integrations** section, click **+ New Access Token**
2. Fill in the form:
   - **Purpose**: `Grade Management` (or any descriptive name)
   - **Expires**: Leave blank or set far in future (e.g., 1 year)
   - **Scopes**: **DO NOT add any scopes** - leave completely blank for full access
3. Click **Generate Token**
4. **Important**: Copy the token immediately (you won't see it again!)

### Step 3: Update canvas-token.json

Replace the token in your `canvas-token.json` file:

```json
{
  "api_url": "https://canvas.mit.edu",
  "api_key": "YOUR_NEW_TOKEN_HERE"
}
```

### Step 4: Test

Run the permission test:

```bash
python3 manage_assignments.py --course-id YOUR_COURSE_ID
# Then select option 5: Test grade upload permissions
```

## Common Token Issues

### Issue 1: Token Has Scope Limitations

**Symptom**: Can read data but not write/modify

**Cause**: Token was created with specific scopes selected

**Fix**: Regenerate token with NO scopes selected (full access)

### Issue 2: Token Expired

**Symptom**: All API calls fail with authentication error

**Cause**: Token had an expiration date

**Fix**: Generate new token without expiration date

### Issue 3: Token Deleted/Revoked

**Symptom**: Authentication errors on all operations

**Cause**: Token was deleted from Canvas settings

**Fix**: Generate new token

## Security Note

**Why leave scopes blank?**

When you leave scopes blank, Canvas gives the token the same permissions as your user account. Since you're a Teacher:
- You can already grade in the Canvas UI
- The API token should have the same permissions
- This is the intended way to use Canvas API tokens for course management

**Is this secure?**

Yes, as long as you:
- Store the token securely (not in public repositories)
- Don't share the token with others
- Use it only from trusted machines
- Consider setting a reasonable expiration (e.g., 1 year) and rotating

## Verification Checklist

After regenerating your token, verify:

- ✓ You are enrolled as a **Teacher** in the course (not just admin)
- ✓ Your token has **no scope limitations** (leave blank when creating)
- ✓ Your token has **not expired**
- ✓ The token is correctly saved in `canvas-token.json`
- ✓ You can create assignments (tests write permission)
- ✓ You can upload grades (tests submission modification)

## Still Having Issues?

If you've regenerated your token and still can't upload grades:

1. **Check Canvas permissions**: Ensure your Teacher role hasn't been customized with restricted permissions
2. **Check assignment settings**: Some assignments may have restricted grading (e.g., moderated grading)
3. **Check course settings**: The course may have grading locked or restricted
4. **Contact Canvas admin**: Your institution may have disabled certain API capabilities

## Testing Without Modifying Grades

The script includes a permission test (Option 5) that:
- Checks your enrollment type
- Verifies you can read assignments
- Verifies you can read submissions
- Does NOT attempt to modify anything

Use this to diagnose issues without risking any data changes.
