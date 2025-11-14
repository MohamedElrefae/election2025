"""
Upload Updated V2 Data to Supabase
Clears existing tables and uploads fresh V2 data with name splitting
"""
import json
import pandas as pd
from supabase import create_client, Client
from tqdm import tqdm
import time
import re

def arabic_to_english_number(text):
    """Convert Arabic numerals to English numerals"""
    if pd.isna(text):
        return text
    text = str(text)
    arabic_numerals = '٠١٢٣٤٥٦٧٨٩'
    english_numerals = '0123456789'
    translation_table = str.maketrans(arabic_numerals, english_numerals)
    return text.translate(translation_table)

def clean_arabic_text(text):
    """Clean Arabic text"""
    if pd.isna(text):
        return ''
    text = str(text)
    # Remove RTL/LTR marks
    text = re.sub(r'[\u202a-\u202e\u200e\u200f]', '', text)
    # Clean whitespace
    text = ' '.join(text.split())
    return text.strip()

def split_arabic_name(full_name):
    """
    Split Arabic name into components
    Returns: (first_name, family_name, middle_names)
    """
    full_name = clean_arabic_text(full_name)
    
    if not full_name:
        return ('', '', '')
    
    parts = full_name.split()
    
    if len(parts) == 0:
        return ('', '', '')
    elif len(parts) == 1:
        return (parts[0], '', '')
    elif len(parts) == 2:
        return (parts[0], parts[1], '')
    else:
        first_name = parts[0]
        family_name = parts[-1]
        middle_names = ' '.join(parts[1:-1])
        return (first_name, family_name, middle_names)

def load_config():
    with open('supabase_config.json', 'r') as f:
        return json.load(f)

def clear_all_data(supabase: Client):
    """Clear all data from both tables"""
    print("\n🗑️  Clearing existing data...")
    
    try:
        # Delete all voters
        response = supabase.table('voters').delete().neq('id', 0).execute()
        print(f"   ✅ Voters table cleared")
    except Exception as e:
        print(f"   ⚠️  Voters clear: {str(e)[:100]}")
    
    try:
        # Delete all locations
        response = supabase.table('locations').delete().neq('location_id', 0).execute()
        print(f"   ✅ Locations table cleared")
    except Exception as e:
        print(f"   ⚠️  Locations clear: {str(e)[:100]}")

def upload_locations(supabase: Client):
    """Upload locations from V2 file"""
    print("\n📍 Loading locations V2...")
    
    df = pd.read_csv('motobus  locationsv2.csv', sep=';', dtype=str)
    df.columns = df.columns.str.strip()
    
    print(f"   Loaded {len(df)} locations")
    
    locations_data = []
    for _, row in df.iterrows():
        try:
            location_id = int(arabic_to_english_number(row['location numer']))
            locations_data.append({
                'location_id': location_id,
                'location_number': str(location_id),
                'location_name': clean_arabic_text(row['location name']),
                'location_address': clean_arabic_text(row['location adress'])
            })
        except Exception as e:
            print(f"   ⚠️  Skipping location: {str(e)[:50]}")
    
    # Upload locations
    print(f"   📤 Uploading {len(locations_data)} locations...")
    supabase.table('locations').insert(locations_data).execute()
    print(f"   ✅ Uploaded {len(locations_data)} locations")
    
    return len(locations_data)

def upload_voters(supabase: Client):
    """Upload voters from V2 file with name splitting"""
    print("\n👥 Loading voters V2...")
    
    df = pd.read_csv('motobus voterv2.csv', sep=';', dtype=str, low_memory=False)
    df.columns = df.columns.str.strip()
    
    print(f"   Loaded {len(df)} voters")
    
    # Convert Arabic numerals
    df['voter_number_clean'] = df['voter number'].apply(arabic_to_english_number)
    df['location_number_clean'] = df['location numer'].apply(arabic_to_english_number)
    
    # Convert to numeric
    df['voter_id'] = pd.to_numeric(df['voter_number_clean'], errors='coerce')
    df['location_id'] = pd.to_numeric(df['location_number_clean'], errors='coerce')
    
    # Remove invalid rows
    df = df.dropna(subset=['voter_id', 'location_id'])
    df = df[df['voter_id'] > 0]
    df = df[df['location_id'] > 0]
    
    print(f"   Valid voters: {len(df)}")
    
    # Split names and prepare data
    print("   ✂️  Splitting names...")
    voters_data = []
    
    for _, row in df.iterrows():
        first_name, family_name, middle_names = split_arabic_name(row['name'])
        
        voters_data.append({
            'voter_id': int(row['voter_id']),
            'full_name': clean_arabic_text(row['name']),
            'first_name': first_name,
            'family_name': family_name,
            'middle_names': middle_names,
            'location_id': int(row['location_id'])
        })
    
    # Upload in batches
    print(f"   📤 Uploading {len(voters_data)} voters in batches...")
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
                    print(f"\n   ❌ Failed: {str(e2)[:80]}")
    
    print(f"\n   ✅ Uploaded {total_uploaded} voters")
    return total_uploaded

def update_voter_counts(supabase: Client):
    """Update voter counts for each location"""
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
    
    try:
        loc_response = supabase.table('locations').select('*', count='exact', head=True).execute()
        voter_response = supabase.table('voters').select('*', count='exact', head=True).execute()
        
        loc_count = loc_response.count if hasattr(loc_response, 'count') else 0
        voter_count = voter_response.count if hasattr(voter_response, 'count') else 0
        
        print(f"\n📊 Database Statistics:")
        print(f"   Locations: {loc_count}")
        print(f"   Voters: {voter_count:,}")
        
        # Top locations
        sample_locs = supabase.table('locations').select('*').order('total_voters', desc=True).limit(5).execute()
        print(f"\n   Top 5 locations:")
        for loc in sample_locs.data:
            print(f"   - #{loc['location_number']}: {loc['location_name'][:45]} ({loc.get('total_voters', 0):,} voters)")
        
        # Sample voters
        sample_voters = supabase.table('voters').select('voter_id, full_name, first_name, family_name').limit(5).execute()
        print(f"\n   Sample voters:")
        for v in sample_voters.data:
            print(f"   - {v['voter_id']}: {v['full_name'][:35]}")
            print(f"     → First: {v['first_name']}, Family: {v['family_name']}")
        
        return True
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def main():
    print("=" * 70)
    print("📤 UPLOAD UPDATED V2 DATA TO SUPABASE")
    print("=" * 70)
    
    config = load_config()
    print(f"\n📡 Connecting to Supabase...")
    
    supabase: Client = create_client(config['url'], config['key'])
    
    # Clear existing data
    clear_all_data(supabase)
    
    # Upload new data
    locations_count = upload_locations(supabase)
    voters_count = upload_voters(supabase)
    
    # Update counts
    update_voter_counts(supabase)
    
    # Verify
    verify_data(supabase)
    
    print("\n" + "=" * 70)
    print("✅ UPLOAD COMPLETE!")
    print("=" * 70)
    print(f"\n📊 Summary:")
    print(f"   ✅ {locations_count} locations uploaded")
    print(f"   ✅ {voters_count:,} voters uploaded")
    print(f"   ✅ Names split: first_name, family_name, middle_names")
    print(f"   ✅ Voter counts updated per location")
    print(f"\n🌐 Refresh your web app to see the updated data!")

if __name__ == "__main__":
    main()
