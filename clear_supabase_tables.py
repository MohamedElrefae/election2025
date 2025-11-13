"""
Clear all data from Supabase tables before inserting new data
"""
import json
from supabase import create_client, Client

def load_config():
    """Load Supabase configuration"""
    with open('supabase_config.json', 'r') as f:
        return json.load(f)

def clear_tables(supabase: Client):
    """Delete all data from voters and locations tables"""
    print("🗑️  Starting to clear Supabase tables...")
    
    try:
        # Delete all voters first (due to foreign key constraint)
        print("\n1️⃣  Deleting all voters...")
        voters_response = supabase.table('voters').delete().neq('id', 0).execute()
        print(f"✅ Voters table cleared successfully")
        
        # Delete all locations
        print("\n2️⃣  Deleting all locations...")
        locations_response = supabase.table('locations').delete().neq('location_id', 0).execute()
        print(f"✅ Locations table cleared successfully")
        
        print("\n✨ All tables cleared! Ready for new data.")
        return True
        
    except Exception as e:
        print(f"\n❌ Error clearing tables: {str(e)}")
        return False

def verify_empty_tables(supabase: Client):
    """Verify that tables are empty"""
    print("\n🔍 Verifying tables are empty...")
    
    try:
        # Check voters count
        voters = supabase.table('voters').select('id', count='exact').execute()
        voters_count = voters.count if hasattr(voters, 'count') else len(voters.data)
        print(f"   Voters count: {voters_count}")
        
        # Check locations count
        locations = supabase.table('locations').select('location_id', count='exact').execute()
        locations_count = locations.count if hasattr(locations, 'count') else len(locations.data)
        print(f"   Locations count: {locations_count}")
        
        if voters_count == 0 and locations_count == 0:
            print("\n✅ Both tables are empty and ready for new data!")
            return True
        else:
            print("\n⚠️  Warning: Tables may still contain data")
            return False
            
    except Exception as e:
        print(f"\n❌ Error verifying tables: {str(e)}")
        return False

def main():
    """Main execution function"""
    print("=" * 60)
    print("🧹 SUPABASE TABLE CLEANER")
    print("=" * 60)
    
    # Load configuration
    config = load_config()
    print(f"\n📡 Connecting to: {config['url']}")
    
    # Create Supabase client
    supabase: Client = create_client(config['url'], config['key'])
    
    # Clear tables
    success = clear_tables(supabase)
    
    if success:
        # Verify tables are empty
        verify_empty_tables(supabase)
    
    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)

if __name__ == "__main__":
    main()
