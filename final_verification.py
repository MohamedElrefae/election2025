"""
Final verification with proper pagination
"""
import json
from supabase import create_client, Client
from collections import Counter

def load_config():
    with open('supabase_config.json', 'r') as f:
        return json.load(f)

def get_all_voters(supabase: Client):
    """Get all voters with pagination"""
    print("📥 Fetching all voters (with pagination)...")
    
    all_voters = []
    page_size = 1000
    offset = 0
    
    while True:
        response = supabase.table('voters').select('location_id').range(offset, offset + page_size - 1).execute()
        if not response.data:
            break
        all_voters.extend(response.data)
        print(f"   Fetched {len(all_voters)} voters so far...")
        offset += page_size
        if len(response.data) < page_size:
            break
    
    print(f"   ✅ Total voters: {len(all_voters)}")
    return all_voters

def update_all_location_counts(supabase: Client, location_counts):
    """Update voter counts for all locations"""
    print("\n🔄 Updating location voter counts...")
    
    locations = supabase.table('locations').select('location_id').execute()
    
    for location in locations.data:
        loc_id = location['location_id']
        count = location_counts.get(loc_id, 0)
        
        supabase.table('locations').update({
            'total_voters': count
        }).eq('location_id', loc_id).execute()
    
    print(f"   ✅ Updated {len(locations.data)} locations")

def main():
    print("=" * 70)
    print("🔍 FINAL VERIFICATION")
    print("=" * 70)
    
    config = load_config()
    supabase = create_client(config['url'], config['key'])
    
    # Get all voters
    all_voters = get_all_voters(supabase)
    
    # Count by location
    location_counts = Counter(v['location_id'] for v in all_voters)
    
    print(f"\n📊 Statistics:")
    print(f"   Total Voters: {len(all_voters)}")
    print(f"   Locations with voters: {len(location_counts)}")
    
    # Update counts
    update_all_location_counts(supabase, location_counts)
    
    # Show top locations
    print(f"\n🏆 Top 10 Locations by Voter Count:")
    for loc_id, count in location_counts.most_common(10):
        # Get location name
        loc = supabase.table('locations').select('location_name').eq('location_id', loc_id).execute()
        name = loc.data[0]['location_name'] if loc.data else 'Unknown'
        print(f"   {loc_id}: {name[:50]} - {count:,} voters")
    
    print("\n" + "=" * 70)
    print("✅ Verification complete!")
    print("=" * 70)

if __name__ == "__main__":
    main()
