"""
Complete solution: Add columns and split names
This script works around the schema limitation by using the existing structure
"""
import json
import pandas as pd
from supabase import create_client, Client
from tqdm import tqdm
import time
import re

def clean_arabic_text(text):
    """Remove RTL marks and extra whitespace"""
    if pd.isna(text):
        return ''
    text = str(text)
    text = re.sub(r'[\u202a-\u202e\u200e\u200f]', '', text)
    text = ' '.join(text.split())
    return text.strip()

def split_arabic_name(full_name):
    """Split Arabic name into first, family, and middle names"""
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

def arabic_to_english_number(text):
    """Convert Arabic numerals to English"""
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

def clear_and_reupload_with_names(supabase: Client):
    """Clear database and re-upload with name splitting"""
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
    
    # Load CSV files
    print("\n📂 Loading CSV files...")
    locations_df = pd.read_csv('motobus  locations.csv', sep=';')
    locations_df.columns = locations_df.columns.str.strip()
    print(f"   Locations: {len(locations_df)}")
    
    voters_df = pd.read_csv('motobus voter.csv', sep=';')
    voters_df.columns = voters_df.columns.str.strip()
    print(f"   Voters: {len(voters_df)}")
    
    # Upload locations
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
    
    # Process voters with name splitting
    print("\n👥 Processing and uploading voters with name splitting...")
    
    # Convert Arabic numerals
    voters_df['voter_number_int'] = voters_df['voter number'].apply(arabic_to_english_number)
    voters_df['voter_number_int'] = pd.to_numeric(voters_df['voter_number_int'], errors='coerce')
    voters_df = voters_df.dropna(subset=['voter_number_int', 'location numer'])
    
    # Split names
    print("   ✂️  Splitting names...")
    name_splits = voters_df['name'].apply(split_arabic_name)
    voters_df['first_name'] = name_splits.apply(lambda x: x[0])
    voters_df['family_name'] = name_splits.apply(lambda x: x[1])
    voters_df['middle_names'] = name_splits.apply(lambda x: x[2])
    
    print(f"\n   📋 Sample name splits:")
    for i in range(min(10, len(voters_df))):
        row = voters_df.iloc[i]
        print(f"   {row['name']}")
        print(f"      → First: {row['first_name']}, Family: {row['family_name']}")
    
    # Prepare voter data
    voters_data = []
    for _, row in voters_df.iterrows():
        voters_data.append({
            'voter_id': int(row['voter_number_int']),
            'full_name': str(row['name']).strip(),
            'location_id': int(row['location numer']),
            'first_name': row['first_name'],
            'family_name': row['family_name'],
            'middle_names': row['middle_names']
        })
    
    # Upload in batches
    print(f"\n   📤 Uploading {len(voters_data)} voters...")
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
                    print(f"\n   ❌ Failed: {str(e2)[:100]}")
    
    print(f"\n   ✅ Uploaded {total_uploaded} voters")
    return total_uploaded

def update_voter_counts(supabase: Client):
    """Update voter counts for locations"""
    print("\n🔄 Updating voter counts...")
    
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
    
    from collections import Counter
    location_counts = Counter(v['location_id'] for v in all_voters)
    
    locations = supabase.table('locations').select('location_id').execute()
    for loc in locations.data:
        loc_id = loc['location_id']
        count = location_counts.get(loc_id, 0)
        supabase.table('locations').update({'total_voters': count}).eq('location_id', loc_id).execute()
    
    print(f"   ✅ Updated {len(locations.data)} locations")

def verify_results(supabase: Client):
    """Verify the results"""
    print("\n🔍 Verifying results...")
    
    # Get counts
    loc_count = supabase.table('locations').select('*', count='exact', head=True).execute().count
    voter_count = supabase.table('voters').select('*', count='exact', head=True).execute().count
    
    print(f"\n📊 Statistics:")
    print(f"   Locations: {loc_count}")
    print(f"   Voters: {voter_count:,}")
    
    # Sample with names
    print(f"\n📋 Sample voters with split names:")
    sample = supabase.table('voters').select('full_name, first_name, family_name, middle_names, location_id').limit(15).execute()
    for voter in sample.data:
        print(f"\n   Full: {voter['full_name']}")
        print(f"   First: {voter['first_name']} | Family: {voter['family_name']}")
        print(f"   Middle: {voter['middle_names']}")
    
    # Family statistics
    print(f"\n👨‍👩‍👧‍👦 Analyzing families...")
    families = []
    offset = 0
    while offset < 10000:
        response = supabase.table('voters').select('family_name').range(offset, offset + 1000 - 1).execute()
        if not response.data:
            break
        families.extend([v['family_name'] for v in response.data if v['family_name']])
        offset += 1000
        if len(response.data) < 1000:
            break
    
    from collections import Counter
    family_counts = Counter(families)
    print(f"\n   Top 10 families (from {len(families)} voters sampled):")
    for family, count in family_counts.most_common(10):
        print(f"   {family}: {count} members")

def main():
    print("=" * 70)
    print("✂️  ADD NAME COLUMNS AND SPLIT NAMES")
    print("=" * 70)
    print("\nThis will:")
    print("  1. Clear existing data")
    print("  2. Re-upload with first_name, family_name, middle_names")
    print("  3. Enable family grouping and better organization")
    print("\n⚠️  Note: This requires the voters table to have these columns:")
    print("     - first_name (TEXT)")
    print("     - family_name (TEXT)")
    print("     - middle_names (TEXT)")
    print("\nPress Enter to continue or Ctrl+C to cancel...")
    input()
    
    config = load_config()
    supabase = create_client(config['url'], config['key'])
    
    # Clear and re-upload with names
    clear_and_reupload_with_names(supabase)
    
    # Update counts
    update_voter_counts(supabase)
    
    # Verify
    verify_results(supabase)
    
    print("\n" + "=" * 70)
    print("✅ COMPLETE!")
    print("=" * 70)
    print("\n💡 Benefits:")
    print("   ✅ Names split into first_name, family_name, middle_names")
    print("   ✅ Can search by first name or family name")
    print("   ✅ Can group voters by family")
    print("   ✅ Better data organization")
    print("\n💡 Next: Update web application to show family grouping")

if __name__ == "__main__":
    main()
