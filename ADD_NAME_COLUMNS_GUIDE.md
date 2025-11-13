# 📝 Guide: Adding Name Columns to Supabase

## Step 1: Add Columns to Database

You need to add three new columns to the `voters` table in Supabase.

### Option A: Using Supabase Dashboard (Recommended)

1. Go to: **https://supabase.com/dashboard**
2. Select your project: **gridbhusfotahmgulgdd**
3. Click **"SQL Editor"** in the left sidebar
4. Click **"New Query"**
5. Copy and paste this SQL:

```sql
-- Add name columns to voters table
ALTER TABLE voters 
ADD COLUMN first_name TEXT,
ADD COLUMN family_name TEXT,
ADD COLUMN middle_names TEXT;

-- Create indexes for better performance
CREATE INDEX idx_voters_family_name ON voters(family_name);
CREATE INDEX idx_voters_first_name ON voters(first_name);

-- Add comments
COMMENT ON COLUMN voters.first_name IS 'First name extracted from full name';
COMMENT ON COLUMN voters.family_name IS 'Family/last name for grouping';
COMMENT ON COLUMN voters.middle_names IS 'Middle names (father, grandfather, etc.)';
```

6. Click the **"Run"** button (or press Ctrl+Enter)
7. Wait for the success message: "Success. No rows returned"

### Option B: Using Supabase Table Editor

1. Go to: **https://supabase.com/dashboard**
2. Select your project: **gridbhusfotahmgulgdd**
3. Click **"Table Editor"** in the left sidebar
4. Select the **"voters"** table
5. Click **"Add Column"** button (3 times for 3 columns)

For each column:
- **Column 1:**
  - Name: `first_name`
  - Type: `text`
  - Default value: (leave empty)
  - Allow nullable: ✓ (checked)

- **Column 2:**
  - Name: `family_name`
  - Type: `text`
  - Default value: (leave empty)
  - Allow nullable: ✓ (checked)

- **Column 3:**
  - Name: `middle_names`
  - Type: `text`
  - Default value: (leave empty)
  - Allow nullable: ✓ (checked)

## Step 2: Verify Columns Were Added

Run this command to verify:

```bash
python test_name_columns.py
```

You should see: ✅ Name columns are supported!

## Step 3: Split Names and Update Data

Once columns are added, run:

```bash
python add_name_columns_and_split.py
```

This will:
1. Clear existing data
2. Re-upload all voters with names split into:
   - `first_name`: First word (e.g., "محمد")
   - `family_name`: Last word (e.g., "مرعى")
   - `middle_names`: Everything in between (e.g., "احمد على")
3. Update voter counts
4. Verify the results

## What This Enables

### Family Grouping
```sql
-- Find all members of a family
SELECT * FROM voters 
WHERE family_name = 'مرعى' 
ORDER BY first_name;
```

### Family Statistics
```sql
-- Count members per family
SELECT family_name, COUNT(*) as members
FROM voters
GROUP BY family_name
ORDER BY members DESC;
```

### Search by First or Last Name
```sql
-- Find all people named محمد
SELECT * FROM voters WHERE first_name = 'محمد';

-- Find all from النجار family
SELECT * FROM voters WHERE family_name = 'النجار';
```

## Expected Results

After completion, you'll have:
- ✅ 188,871 voters with split names
- ✅ Ability to group by family
- ✅ Better search capabilities
- ✅ Family statistics

### Top Families (Expected):
1. مرعى - ~1,700 members
2. النجار - ~1,600 members
3. محمد - ~1,500 members
4. درويش - ~1,400 members
5. بدر - ~1,400 members

## Troubleshooting

### "Column already exists" error
- Columns were already added, proceed to Step 3

### "Permission denied" error
- Make sure you're logged into the correct Supabase account
- Check that you have admin access to the project

### "Schema cache" error
- Wait 30 seconds and try again
- Supabase needs time to update its cache

## Need Help?

If you encounter issues:
1. Check the Supabase Dashboard for error messages
2. Verify you're in the correct project
3. Make sure the SQL ran successfully
4. Try refreshing the Supabase page

---

**Ready?** Follow Step 1 above, then run the scripts!
