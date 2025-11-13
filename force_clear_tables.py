"""
Force clear all data from Supabase tables using alternative methods
"""
import json
from supabase import create_client, Client

def load_config():
    """Load Supabase configuration"""
    with open('supabase_config.json', 'r') as f:
        return json.load(f)

def force_clear_tables(supabase: Client):
    """Force delete all data from tables"""
    print("🗑️  Force clearing all data from Supabase tables...")
    
    try:
        # Method 1: Delete voters with gte filter
        print("\n1️⃣  Clearing voters table...")
        try:
            supabase.table('voters').delete().gte('id', 0).execute()
            print("✅ Voters cleared")
        except Exception as e:
            print(f"   Voters already empty or error: {e}")
        
        # Method 2: Delete locations with gte filter
        print("\n2️⃣  Clearing locations table...")
        try:
            supabase.table('locations').delete().gte('location_id', 0).execute()
            print("✅ Locations cleared")
        except Exception as e:
            print(f"   Locations already empty or error: {e}")
        
        print("\n✨ Force clear completed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False

def get_and_delete_all(supabase: Client):
    """Get all records and delete them one by one if needed"""
    print("\n🔄 Alternative method: Fetching and deleting individually...")
    
    try:
        # Get all locations
        locations = supabase.table('locations').select('location_id').execute()
        if locations.data:
            print(f"   Found {len(locations.data)} locations to delete")
            for loc in locations.data:
                supabase.table('locations').delete().eq('location_id', loc['location_id']).execute()
            print("✅ All locations deleted individually")
        else:
            print("   No locations found")
            
    except Exception as e:
        print(f"   Error: {e}")

def verify_tables(supabase: Client):
    """Final verification"""
    print("\n🔍 Final verification...")
    
    try:
        voters = supabase.table('voters').select('*').execute()
        locations = supabase.table('locations').select('*').execute()
        
        voters_count = len(voters.data) if voters.data else 0
        locations_count = len(locations.data) if locations.data else 0
        
        print(f"   Voters: {voters_count}")
        print(f"   Locations: {locations_count}")
        
        if voters_count == 0 and locations_count == 0:
            print("\n✅ SUCCESS! Both tables are completely empty!")
            return True
        else:
            print(f"\n⚠️  Still have data remaining")
            if locations_count > 0:
                print(f"   Remaining locations: {locations.data}")
            return False
            
    except Exception as e:
        print(f"   Error: {e}")
        return False

def main():
    """Main execution"""
    print("=" * 60)
    print("🧹 FORCE CLEAR SUPABASE TABLES")
    print("=" * 60)
    
    config = load_config()
    print(f"\n📡 Connecting to: {config['url']}")
    
    supabase: Client = create_client(config['url'], config['key'])
    
    # Try force clear
    force_clear_tables(supabase)
    
    # Verify
    if not verify_tables(supabase):
        # Try alternative method
        get_and_delete_all(supabase)
        verify_tables(supabase)
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
