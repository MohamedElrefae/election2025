"""
Interactive setup for family name splitting
"""
import json
from supabase import create_client, Client
import webbrowser

def load_config():
    with open('supabase_config.json', 'r') as f:
        return json.load(f)

def main():
    print("=" * 70)
    print("👨‍👩‍👧‍👦 FAMILY NAME SETUP - Interactive Guide")
    print("=" * 70)
    
    print("\nThis setup will enable family grouping by splitting names into:")
    print("  • First Name (e.g., محمد)")
    print("  • Family Name (e.g., مرعى)")
    print("  • Middle Names (e.g., احمد على)")
    
    print("\n" + "=" * 70)
    print("STEP 1: Add Columns to Supabase")
    print("=" * 70)
    
    print("\nWe need to add 3 columns to your voters table.")
    print("\nOption 1: Open Supabase Dashboard now? (y/n): ", end='')
    choice = input().lower()
    
    if choice == 'y':
        url = "https://supabase.com/dashboard/project/gridbhusfotahmgulgdd/editor"
        print(f"\n🌐 Opening: {url}")
        try:
            webbrowser.open(url)
        except:
            print(f"   Please open this URL manually: {url}")
    
    print("\n📋 Copy and paste this SQL in the SQL Editor:")
    print("\n" + "-" * 70)
    
    sql = """ALTER TABLE voters 
ADD COLUMN first_name TEXT,
ADD COLUMN family_name TEXT,
ADD COLUMN middle_names TEXT;

CREATE INDEX idx_voters_family_name ON voters(family_name);
CREATE INDEX idx_voters_first_name ON voters(first_name);"""
    
    print(sql)
    print("-" * 70)
    
    print("\n📝 Instructions:")
    print("  1. Go to Supabase Dashboard > SQL Editor")
    print("  2. Click 'New Query'")
    print("  3. Paste the SQL above")
    print("  4. Click 'Run' (or press Ctrl+Enter)")
    print("  5. Wait for 'Success. No rows returned' message")
    
    print("\n✅ Once done, press Enter to continue...")
    input()
    
    # Test if columns exist
    print("\n🔍 Testing if columns were added...")
    config = load_config()
    supabase = create_client(config['url'], config['key'])
    
    try:
        test_data = {
            'voter_id': 99999,
            'full_name': 'Test',
            'location_id': 76,
            'first_name': 'T',
            'family_name': 'T',
            'middle_names': ''
        }
        supabase.table('voters').insert(test_data).execute()
        supabase.table('voters').delete().eq('voter_id', 99999).eq('location_id', 76).execute()
        
        print("✅ Columns added successfully!")
        
        print("\n" + "=" * 70)
        print("STEP 2: Split Names and Update Data")
        print("=" * 70)
        
        print("\nReady to split names and update database?")
        print("This will:")
        print("  • Clear existing voter data")
        print("  • Re-upload with split names")
        print("  • Take about 5-10 minutes")
        
        print("\nContinue? (y/n): ", end='')
        choice = input().lower()
        
        if choice == 'y':
            print("\n🚀 Starting name splitting process...")
            print("   Run: python add_name_columns_and_split.py")
            print("\nOr press Enter to run it now...")
            input()
            
            import subprocess
            subprocess.run(['python', 'add_name_columns_and_split.py'])
        else:
            print("\n💡 When ready, run: python add_name_columns_and_split.py")
        
    except Exception as e:
        error_msg = str(e)
        if 'family_name' in error_msg or 'first_name' in error_msg:
            print("❌ Columns not found. Please make sure you:")
            print("   1. Ran the SQL in Supabase Dashboard")
            print("   2. Saw the success message")
            print("   3. Waited 30 seconds for cache to update")
            print("\n💡 Try again in 30 seconds")
        else:
            print(f"❌ Error: {error_msg[:200]}")
    
    print("\n" + "=" * 70)
    print("Setup guide complete!")
    print("=" * 70)

if __name__ == "__main__":
    main()
