"""
Apply schema changes to add name columns
"""
import json
from supabase import create_client, Client
import requests

def load_config():
    with open('supabase_config.json', 'r') as f:
        return json.load(f)

def apply_schema_via_api(config):
    """Apply schema changes using Supabase REST API"""
    print("=" * 70)
    print("🔧 APPLYING SCHEMA CHANGES")
    print("=" * 70)
    
    print("\n⚠️  IMPORTANT: Schema changes need to be applied via Supabase Dashboard")
    print("\nPlease follow these steps:")
    print("\n1. Go to: https://supabase.com/dashboard")
    print("2. Select your project: gridbhusfotahmgulgdd")
    print("3. Click 'SQL Editor' in the left menu")
    print("4. Click 'New Query'")
    print("5. Copy and paste this SQL:\n")
    
    sql = """
-- Add name columns to voters table
ALTER TABLE voters 
ADD COLUMN IF NOT EXISTS first_name TEXT,
ADD COLUMN IF NOT EXISTS family_name TEXT,
ADD COLUMN IF NOT EXISTS middle_names TEXT;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_voters_family_name ON voters(family_name);
CREATE INDEX IF NOT EXISTS idx_voters_first_name ON voters(first_name);
"""
    
    print("-" * 70)
    print(sql)
    print("-" * 70)
    
    print("\n6. Click 'Run' button")
    print("7. Wait for success message")
    print("\n✅ Once done, press Enter to continue...")
    input()
    
    print("\n✅ Schema changes applied!")

def main():
    config = load_config()
    apply_schema_via_api(config)
    
    print("\n💡 Next step: Run 'python split_names_and_update.py'")

if __name__ == "__main__":
    main()
