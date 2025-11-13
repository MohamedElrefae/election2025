#!/usr/bin/env python3
"""
Verify Egypt 2025 Election Data in Supabase
"""

import json
from supabase import create_client, Client

def verify_data():
    """Verify the data in Supabase"""
    
    print("🔍 Verifying Egypt 2025 Election Data in Supabase...")
    
    # Load configuration
    with open('supabase_config.json', 'r') as f:
        config = json.load(f)
    
    # Connect to Supabase
    supabase: Client = create_client(config['url'], config['key'])
    
    try:
        # Count locations
        locations_response = supabase.table('locations').select('location_id').execute()
        locations_count = len(locations_response.data)
        
        # Count voters
        voters_response = supabase.table('voters').select('id').execute()
        voters_count = len(voters_response.data)
        
        print(f"✅ Database Connection Successful!")
        print(f"📍 Locations in database: {locations_count:,}")
        print(f"👥 Voters in database: {voters_count:,}")
        
        # Get sample locations
        sample_locations = supabase.table('locations').select('*').limit(5).execute()
        
        print(f"\n📋 Sample Locations:")
        for location in sample_locations.data:
            print(f"  Committee {location['location_number']}: {location['location_name']}")
            print(f"    Address: {location['location_address']}")
            print(f"    Voters: {location['total_voters']}")
            print()
        
        # Get sample voters
        sample_voters = supabase.table('voters').select('*').limit(5).execute()
        
        print(f"📋 Sample Voters:")
        for voter in sample_voters.data:
            print(f"  ID {voter['voter_id']}: {voter['full_name']}")
            print(f"    Location: {voter['location_id']}, Page: {voter['source_page']}")
        
        # Test a query
        print(f"\n🔍 Testing Query - Voters in Committee 67:")
        committee_67_voters = supabase.table('voters').select('full_name').eq('location_id', 14).limit(3).execute()
        
        for voter in committee_67_voters.data:
            print(f"  - {voter['full_name']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    verify_data()