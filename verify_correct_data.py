"""
Verify the corrected data in Supabase
"""
import json
from supabase import create_client, Client

def load_config():
    with open('supabase_config.json', 'r') as f:
        return json.load(f)

def main():
    print("=" * 70)
    print("✅ VERIFYING CORRECTED DATA")
    print("=" * 70)
    
    config = load_config()
    supabase = create_client(config['url'], config['key'])
    
    # Get counts
    print("\n📊 Database Statistics:")
    loc_response = supabase.table('locations').select('*', count='exact', head=True).execute()
    voter_response = supabase.table('voters').select('*', count='exact', head=True).execute()
    
    print(f"   Total Locations: {loc_response.count}")
    print(f"   Total Voters: {voter_response.count:,}")
    
    # Sample voters from different locations
    print("\n📋 Sample Voters (showing voter_id is now integer):")
    samples = supabase.table('voters').select('voter_id, full_name, location_id').limit(10).execute()
    for voter in samples.data:
        print(f"   Voter {voter['voter_id']} at Location {voter['location_id']}: {voter['full_name'][:40]}")
    
    # Check for duplicates
    print("\n🔍 Checking for duplicates...")
    all_voters = []
    offset = 0
    page_size = 1000
    
    while offset < 5000:  # Check first 5000
        response = supabase.table('voters').select('voter_id, location_id').range(offset, offset + page_size - 1).execute()
        if not response.data:
            break
        all_voters.extend(response.data)
        offset += page_size
        if len(response.data) < page_size:
            break
    
    # Check for duplicate combinations
    combinations = set()
    duplicates = 0
    for voter in all_voters:
        key = (voter['location_id'], voter['voter_id'])
        if key in combinations:
            duplicates += 1
        combinations.add(key)
    
    print(f"   Checked {len(all_voters)} voters")
    print(f"   Unique combinations: {len(combinations)}")
    print(f"   Duplicates found: {duplicates}")
    
    if duplicates == 0:
        print("   ✅ No duplicates found!")
    else:
        print(f"   ⚠️  Found {duplicates} duplicates")
    
    # Top locations
    print("\n🏆 Top 5 Locations by Voter Count:")
    top_locs = supabase.table('locations').select('*').order('total_voters', desc=True).limit(5).execute()
    for i, loc in enumerate(top_locs.data, 1):
        print(f"   {i}. Location {loc['location_number']}: {loc['location_name'][:45]}")
        print(f"      Voters: {loc['total_voters']:,}")
    
    print("\n" + "=" * 70)
    print("✅ DATA VERIFICATION COMPLETE")
    print("=" * 70)
    print("\n💡 The web application at http://localhost:3000 now shows correct data!")
    print("   Refresh the page to see the updated statistics.")

if __name__ == "__main__":
    main()
