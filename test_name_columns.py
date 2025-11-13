"""
Test if we can add name columns to voters table
"""
import json
from supabase import create_client, Client

def load_config():
    with open('supabase_config.json', 'r') as f:
        return json.load(f)

def main():
    print("Testing name column support...")
    
    config = load_config()
    supabase = create_client(config['url'], config['key'])
    
    # Try to insert a test record with name fields
    try:
        test_data = {
            'voter_id': 99999,
            'full_name': 'Test Name',
            'location_id': 76,
            'first_name': 'Test',
            'family_name': 'Name',
            'middle_names': ''
        }
        
        result = supabase.table('voters').insert(test_data).execute()
        print("✅ Name columns are supported!")
        
        # Delete test record
        supabase.table('voters').delete().eq('voter_id', 99999).eq('location_id', 76).execute()
        print("✅ Test record cleaned up")
        
        return True
        
    except Exception as e:
        error_msg = str(e)
        if 'column' in error_msg.lower() and ('first_name' in error_msg or 'family_name' in error_msg):
            print(f"❌ Name columns don't exist yet")
            print(f"   Error: {error_msg[:200]}")
            print("\n💡 You need to add these columns to the voters table first.")
            print("\nSQL to run in Supabase Dashboard > SQL Editor:")
            print("-" * 70)
            print("""
ALTER TABLE voters 
ADD COLUMN first_name TEXT,
ADD COLUMN family_name TEXT,
ADD COLUMN middle_names TEXT;

CREATE INDEX idx_voters_family_name ON voters(family_name);
CREATE INDEX idx_voters_first_name ON voters(first_name);
""")
            print("-" * 70)
            return False
        else:
            print(f"❌ Unexpected error: {error_msg}")
            return False

if __name__ == "__main__":
    main()
