"""
Verify upload and fix voter counts
"""
import json
from supabase import create_client, Client
from collections import Counter

def load_config():
    with open('supabase_config.json', 'r') as f:
        return json.load(f)

def verify_and_fix(supabase: Client):
    print("🔍 Verifying and fixing data...")
    
    # Get all voters
    print("\n1️⃣ Fetching all voters...")
    voters = supabase.table('voters').select('location_id').execute()
    print(f"   Total voters: {len(voters.data)}")
    
    # Count voters per location
    location_counts = Counter(v['location_id'] for v in voters.data)
    print(f"   Unique locations with voters: {len(location_counts)}")
    
    # Get all locations
    print("\n2️⃣ Fetching all locations...")
    locations = supabase.table('locations').select('*').execute()
    print(f"   Total locations: {len(locations.data)}")
    
    # Update each location with correct voter count
    print("\n3️⃣ Updating voter counts...")
    for location in locations.data:
        loc_id = location['location_id']
        count = location_counts.get(loc_id, 0)
        
        if location['total_voters'] != count:
            supabase.table('locations').update({
                'total_voters': count
            }).eq('location_id', loc_id).execute()
            print(f"   Updated location {loc_id}: {count} voters")
    
    print("\n✅ All counts updated!")
    
    # Show summary
    print("\n📊 Final Summary:")
    print(f"   Total Locations: {len(locations.data)}")
    print(f"   Total Voters: {len(voters.data)}")
    print(f"   Locations with voters: {len(location_counts)}")
    
    # Show top 5 locations by voter count
    print("\n🏆 Top 5 Locations by Voter Count:")
    for loc_id, count in location_counts.most_common(5):
        loc_info = next((l for l in locations.data if l['location_id'] == loc_id), None)
        if loc_info:
            print(f"   {loc_id}: {loc_info['location_name'][:50]} - {count} voters")

def main():
    print("=" * 70)
    print("🔧 VERIFY AND FIX VOTER COUNTS")
    print("=" * 70)
    
    config = load_config()
    supabase = create_client(config['url'], config['key'])
    
    verify_and_fix(supabase)
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
