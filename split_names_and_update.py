"""
Split voter names into first_name, family_name, and middle_names
Then update Supabase database
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
        # First name is first part
        first_name = parts[0]
        # Family name is last part
        family_name = parts[-1]
        # Middle names are everything in between
        middle_names = ' '.join(parts[1:-1])
        return (first_name, family_name, middle_names)

def load_config():
    with open('supabase_config.json', 'r') as f:
        return json.load(f)

def update_schema(supabase: Client):
    """Add new columns to voters table"""
    print("\n🔧 Updating database schema...")
    
    # Read SQL file
    with open('update_schema_with_names.sql', 'r', encoding='utf-8') as f:
        sql_commands = f.read()
    
    print("   ℹ️  Please run the SQL commands manually in Supabase SQL Editor:")
    print("   1. Go to Supabase Dashboard > SQL Editor")
    print("   2. Copy and paste the contents of 'update_schema_with_names.sql'")
    print("   3. Execute the SQL")
    print("\n   Press Enter when done...")
    input()

def update_voter_names(supabase: Client):
    """Fetch all voters, split names, and update"""
    print("\n📥 Fetching all voters...")
    
    all_voters = []
    offset = 0
    page_size = 1000
    
    while True:
        response = supabase.table('voters').select('id, full_name').range(offset, offset + page_size - 1).execute()
        if not response.data:
            break
        all_voters.extend(response.data)
        print(f"   Fetched {len(all_voters)} voters...")
        offset += page_size
        if len(response.data) < page_size:
            break
    
    print(f"\n✅ Total voters to process: {len(all_voters)}")
    
    # Split names
    print("\n✂️  Splitting names...")
    updates = []
    
    for voter in tqdm(all_voters, desc="Processing names"):
        first_name, family_name, middle_names = split_arabic_name(voter['full_name'])
        updates.append({
            'id': voter['id'],
            'first_name': first_name,
            'family_name': family_name,
            'middle_names': middle_names
        })
    
    # Update database in batches
    print("\n📤 Updating database...")
    batch_size = 100
    updated_count = 0
    
    for i in tqdm(range(0, len(updates), batch_size), desc="Updating"):
        batch = updates[i:i+batch_size]
        
        for update in batch:
            try:
                supabase.table('voters').update({
                    'first_name': update['first_name'],
                    'family_name': update['family_name'],
                    'middle_names': update['middle_names']
                }).eq('id', update['id']).execute()
                updated_count += 1
            except Exception as e:
                print(f"\n   ⚠️  Error updating voter {update['id']}: {str(e)[:100]}")
        
        time.sleep(0.1)  # Small delay to avoid rate limits
    
    print(f"\n✅ Updated {updated_count} voters")

def verify_split_names(supabase: Client):
    """Verify the name splitting"""
    print("\n🔍 Verifying name splits...")
    
    # Get sample
    sample = supabase.table('voters').select('full_name, first_name, family_name, middle_names').limit(20).execute()
    
    print("\n📋 Sample Results:")
    for voter in sample.data:
        print(f"\nFull Name: {voter['full_name']}")
        print(f"  First: {voter['first_name']}")
        print(f"  Middle: {voter['middle_names']}")
        print(f"  Family: {voter['family_name']}")
    
    # Get family statistics
    print("\n👨‍👩‍👧‍👦 Top 10 Family Names:")
    
    # Count family names (we'll do this client-side since we can't run complex SQL)
    all_families = []
    offset = 0
    page_size = 1000
    
    print("   Fetching family data...")
    while offset < 10000:  # Sample first 10k
        response = supabase.table('voters').select('family_name, location_id').range(offset, offset + page_size - 1).execute()
        if not response.data:
            break
        all_families.extend(response.data)
        offset += page_size
        if len(response.data) < page_size:
            break
    
    from collections import Counter
    family_counts = Counter(f['family_name'] for f in all_families if f['family_name'])
    
    print(f"\n   Top families (from {len(all_families)} voters sampled):")
    for family, count in family_counts.most_common(10):
        print(f"   {family}: {count} members")

def main():
    print("=" * 70)
    print("✂️  SPLIT NAMES INTO FIRST NAME AND FAMILY NAME")
    print("=" * 70)
    
    config = load_config()
    supabase = create_client(config['url'], config['key'])
    
    # Update schema
    update_schema(supabase)
    
    # Split and update names
    update_voter_names(supabase)
    
    # Verify
    verify_split_names(supabase)
    
    print("\n" + "=" * 70)
    print("✅ NAME SPLITTING COMPLETE!")
    print("=" * 70)
    print("\n💡 Benefits:")
    print("   - Can now search by first name or family name")
    print("   - Can group voters by family")
    print("   - Better data organization")
    print("   - Family statistics available")

if __name__ == "__main__":
    main()
