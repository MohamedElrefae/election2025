"""
Clean Supabase and re-upload with correct data handling
"""
import json
import pandas as pd
from supabase import create_client, Client
from tqdm import tqdm
import time

def arabic_to_english_number(text):
    """Convert Arabic numerals to English numerals"""
    if pd.isna(text):
        return text
    text = str(text)
    arabic_numerals = '٠١٢٣٤٥٦٧٨٩'
    english_numerals = '0123456789'
    translation_table = str.maketrans(arabic_numerals, english_numerals)
    return text.translate(translation_table)

def load_config():
    with open('supabase_config.json', 'r') as f:
        return json.load(f)

def clear_all_data(supabase: Client):
    """Clear all existing data"""
    print("\n🗑️  Clearing existing data...")
    try:
        supabase.table('voters').delete().gte('id', 0).execute()
        print("   ✅ Voters cleared")
    except:
        pass
    
    try:
        supabase.table('locations').delete().gte('location_id', 0).execute()
        print("   ✅ Locations cleared")
    except:
        pass

def upload_locations(supabase: Client, locations_df):
    """Upload locations"""
    print("\n📍 Uploading locations...")
    
    locations_data = []
    for _, row in locations_df.iterrows():
        location_id = int(row['location numer'])
        locations_data.append({
            'location_id': location_id,
            'location_number': str(location_id),
            'location_name': str(row['location name']).strip(),
            'location_address': str(row['location adress']).strip()
        })
    
    supabase.table('locations').insert(locations_data).execute()
    print(f"   ✅ Uploaded {len(locations_data)} locations")

def upload_voters(supabase: Client, voters_df):
    """Upload voters with proper handling"""
    print("\n👥 Uploading voters...")
    
    # Convert Arabic numerals
    voters_df['voter_number_int'] = voters_df['voter number'].apply(arabic_to_english_number)
    voters_df['voter_number_int'] = pd.to_numeric(voters_df['voter_number_int'], errors='coerce')
    
    # Remove any rows with invalid data
    voters_df = voters_df.dropna(subset=['voter_number_int', 'location numer'])
    
    print(f"   Total voters to upload: {len(voters_df)}")
    
    voters_data = []
    for _, row in voters_df.iterrows():
        voters_data.append({
            'voter_id': int(row['voter_number_int']),
            'full_name': str(row['name']).strip(),
            'location_id': int(row['location numer'])
        })
    
    # Upload in batches
    batch_size = 500
    total_uploaded = 0
    
    for i in tqdm(range(0, len(voters_data), batch_size), desc="Uploading"):
        batch = voters_data[i:i+batch_size]
        try:
            supabase.table('voters').insert(batch).execute()
            total_uploaded += len(batch)
            time.sleep(0.3)
        except Exception as e:
            # Try smaller batches
            for j in range(0, len(batch), 100):
                mini_batch = batch[j:j+100]
                try:
                    supabase.table('voters').insert(mini_batch).execute()
                    total_uploaded += len(mini_batch)
                    time.sleep(0.2)
                except Exception as e2:
                    print(f"\n   ❌ Failed batch: {str(e2)[:100]}")
    
    print(f"\n   ✅ Uploaded {total_uploaded} voters")
    return total_uploaded

def update_voter_counts(supabase: Client):
    """Update voter counts for locations"""
    print("\n🔄 Updating voter counts...")
    
    # Get all voters
    all_voters = []
    offset = 0
    page_size = 1000
    
    while True:
        response = supabase.table('voters').select('location_id').range(offset, offset + page_size - 1).execute()
        if not response.data:
            break
        all_voters.extend(response.data)
        offset += page_size
        if len(response.data) < page_size:
            break
    
    # Count by location
    from collections import Counter
    location_counts = Counter(v['location_id'] for v in all_voters)
    
    # Update each location
    locations = supabase.table('locations').select('location_id').execute()
    for loc in locations.data:
        loc_id = loc['location_id']
        count = location_counts.get(loc_id, 0)
        supabase.table('locations').update({'total_voters': count}).eq('location_id', loc_id).execute()
    
    print(f"   ✅ Updated {len(locations.data)} locations")

def verify_data(supabase: Client):
    """Verify uploaded data"""
    print("\n🔍 Verifying data...")
    
    # Count records
    loc_count = supabase.table('locations').select('*', count='exact', head=True).execute().count
    voter_count = supabase.table('voters').select('*', count='exact', head=True).execute().count
    
    print(f"\n📊 Final Statistics:")
    print(f"   Locations: {loc_count}")
    print(f"   Voters: {voter_count:,}")
    
    # Show sample
    sample_locs = supabase.table('locations').select('*').order('total_voters', desc=True).limit(5).execute()
    print(f"\n   Top 5 locations by voter count:")
    for loc in sample_locs.data:
        print(f"   - {loc['location_number']}: {loc['location_name'][:40]} ({loc['total_voters']:,} voters)")

def main():
    print("=" * 70)
    print("🔄 CLEAN AND RE-UPLOAD ELECTION DATA")
    print("=" * 70)
    
    config = load_config()
    supabase = create_client(config['url'], config['key'])
    
    # Clear existing data
    clear_all_data(supabase)
    
    # Load CSV files
    print("\n📂 Loading CSV files...")
    locations_df = pd.read_csv('motobus  locations.csv', sep=';')
    locations_df.columns = locations_df.columns.str.strip()
    print(f"   Locations: {len(locations_df)}")
    
    voters_df = pd.read_csv('motobus voter.csv', sep=';')
    voters_df.columns = voters_df.columns.str.strip()
    print(f"   Voters: {len(voters_df)}")
    
    # Upload
    upload_locations(supabase, locations_df)
    upload_voters(supabase, voters_df)
    update_voter_counts(supabase)
    verify_data(supabase)
    
    print("\n" + "=" * 70)
    print("✅ DATA UPLOAD COMPLETE!")
    print("=" * 70)
    print("\n💡 Note: Voter IDs are now correctly stored as integers")
    print("   Each location has voters numbered from 1 to N")
    print("   The combination of location_id + voter_id is unique")

if __name__ == "__main__":
    main()
