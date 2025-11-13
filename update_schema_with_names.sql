-- Add first_name and family_name columns to voters table

-- Add new columns
ALTER TABLE voters 
ADD COLUMN IF NOT EXISTS first_name TEXT,
ADD COLUMN IF NOT EXISTS family_name TEXT,
ADD COLUMN IF NOT EXISTS middle_names TEXT;

-- Create index on family_name for efficient grouping
CREATE INDEX IF NOT EXISTS idx_voters_family_name ON voters(family_name);
CREATE INDEX IF NOT EXISTS idx_voters_first_name ON voters(first_name);

-- Create a view for family grouping
CREATE OR REPLACE VIEW voters_by_family AS
SELECT 
    family_name,
    COUNT(*) as family_member_count,
    location_id,
    l.location_name,
    l.location_number,
    array_agg(full_name ORDER BY voter_id) as family_members,
    array_agg(voter_id ORDER BY voter_id) as voter_ids
FROM voters v
JOIN locations l ON v.location_id = l.location_id
WHERE family_name IS NOT NULL AND family_name != ''
GROUP BY family_name, location_id, l.location_name, l.location_number
ORDER BY family_member_count DESC, family_name;

-- Create a view for family statistics
CREATE OR REPLACE VIEW family_statistics AS
SELECT 
    family_name,
    COUNT(DISTINCT location_id) as locations_count,
    COUNT(*) as total_members,
    array_agg(DISTINCT location_id ORDER BY location_id) as location_ids
FROM voters
WHERE family_name IS NOT NULL AND family_name != ''
GROUP BY family_name
HAVING COUNT(*) > 1
ORDER BY total_members DESC, family_name;

-- Comments
COMMENT ON COLUMN voters.first_name IS 'First name extracted from full name';
COMMENT ON COLUMN voters.family_name IS 'Family/last name extracted from full name';
COMMENT ON COLUMN voters.middle_names IS 'Middle names (father, grandfather, etc.)';
