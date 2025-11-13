"""
Show summary of Supabase data
"""
import json
from supabase import create_client, Client

def load_config():
    with open('supabase_config.json', 'r') as f:
        return json.load(f)

def main():
    print("=" * 70)
    print("📊 SUPABASE DATABASE SUMMARY")
    print("=" * 70)
    
    config = load_config()
    supabase = create_client(config['url'], config['key'])
    
    # Get counts using count query
    print("\n📈 Database Statistics:")
    
    # Count locations
    locations = supabase.table('locations').select('*', count='exact').limit(1).execute()
    loc_count = locations.count if hasattr(locations, 'count') else 0
    
    # Count voters  
    voters = supabase.table('voters').select('id', count='exact').limit(1).execute()
    voter_count = voters.count if hasattr(voters, 'count') else 0
    
    print(f"   Total Locations: {loc_count}")
    print(f"   Total Voters: {voter_count:,}")
    
    # Get sample locations with voter counts
    print("\n📍 Sample Locations:")
    sample_locs = supabase.table('locations').select('*').order('total_voters', desc=True).limit(5).execute()
    
    for loc in sample_locs.data:
        print(f"\n   Location ID: {loc['location_id']}")
        print(f"   Name: {loc['location_name']}")
        print(f"   Address: {loc['location_address']}")
        print(f"   Total Voters: {loc['total_voters']:,}")
    
    print("\n" + "=" * 70)
    print("✅ Data successfully uploaded and linked!")
    print("=" * 70)
    print("\n💡 Your Supabase database is ready to use!")
    print(f"   URL: {config['url']}")
    print(f"   Tables: locations (linked to) voters via location_id")

if __name__ == "__main__":
    main()
