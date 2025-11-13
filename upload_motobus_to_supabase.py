"""
Upload Motobus locations and voters data to Supabase
"""
import json
import pandas as pd
from supabase import create_client, Client
from tqdm import tqdm

def load_config():
    """Load Supabase configuration"""
    with open('supabase_config.json', 'r') as f:
        return json.load(f)

def load_data():
    """Load locations and voters CSV files"""
    print("📂 Loading CSV files...")
    
    # Load locations
    locations_df = pd.read_csv('motobus  locations.csv', sep=';')
    locations_df = locations_df[['location numer', 'location adress', 'location name ']]
    locations_df.columns = ['location_number', 'location_address', 'location_name']
    locations_df = locations_df.dropna(subset=['location_number'])
    
    print(f"   ✅ Loaded {len(locations_df)} locations")
    
    # Load voters
    voters_df = pd.read_csv('motobus voter.csv', sep=';')
    voters_df = voters_df[['name ', 'voter number', 'location numer']]
    voters_df.columns = ['full_name', 'voter_number', 'location_number']
    voters_df = voters_df.dropna(subset=['voter_number', 'location_number'])
    
    print(f"   ✅ Loaded {len(voters_df)} voters")
    
    return locations_df, voters_df

def upload_locations(supabase: Client, locations_df):
    """Upload locations to Supabase"""
    print("\n📍 Uploading locations...")
    
    locations_data = []
    for _, row in locations_df.iterrows():
        location_id = int(row['location_number'])
        locations_data.append({
            'location_id': location_id,
            'location_number': str(location_id),
            'location_name': str(row['location_name']).strip(),
            'location_address': str(row['location_address']).strip()
        })
    
    # Upload in batches
    batch_size = 100
    for i in tqdm(range(0, len(locations_data), batch_size), desc="Uploading locations"):
        batch = locations_data[i:i+batch_size]
        supabase.table('locations').insert(batch).execute()
    
    print(f"   ✅ Uploaded {len(locations_data)} locations")
    return True

def upload_voters(supabase: Client, voters_df):
    """Upload voters to Supabase"""
    print("\n👥 Uploading voters...")
    
    voters_data = []
    for _, row in voters_df.iterrows():
        voters_data.append({
            'voter_id': int(row['voter_number']),
            'full_name': str(row['full_name']).strip(),
            'location_id': int(row['location_number'])
        })
    
    # Upload in smaller batches to avoid API limits
    batch_size = 500
    total_uploaded = 0
    failed_batches = []
    
    for i in tqdm(range(0, len(voters_data), batch_size), desc="Uploading voters"):
        batch = voters_data[i:i+batch_size]
        try:
            supabase.table('voters').insert(batch).execute()
            total_uploaded += len(batch)
        except Exception as e:
            error_msg = str(e)
            if '500' in error_msg or 'Internal server error' in error_msg:
                # Server error - try smaller batch
                print(f"\n   ⚠️  Server error in batch {i//batch_size + 1}, trying smaller batches...")
                for j in range(0, len(batch), 100):
                    mini_batch = batch[j:j+100]
                    try:
                        supabase.table('voters').insert(mini_batch).execute()
                        total_uploaded += len(mini_batch)
                    except Exception as e2:
                        failed_batches.append((i+j, mini_batch))
                        print(f"   ❌ Failed mini-batch at {i+j}")
            else:
                failed_batches.append((i, batch))
                print(f"\n   ❌ Error in batch {i//batch_size + 1}: {error_msg[:100]}")
    
    print(f"   ✅ Uploaded {total_uploaded} voters")
    if failed_batches:
        print(f"   ⚠️  {len(failed_batches)} batches failed")
    
    return total_uploaded

def update_location_voter_counts(supabase: Client):
    """Update total_voters count for each location"""
    print("\n🔄 Updating voter counts for locations...")
    
    try:
        # Get voter counts per location
        voters = supabase.table('voters').select('location_id').execute()
        
        if voters.data:
            location_counts = {}
            for voter in voters.data:
                loc_id = voter['location_id']
                location_counts[loc_id] = location_counts.get(loc_id, 0) + 1
            
            # Update each location
            for loc_id, count in tqdm(location_counts.items(), desc="Updating counts"):
                supabase.table('locations').update({
                    'total_voters': count
                }).eq('location_id', loc_id).execute()
            
            print(f"   ✅ Updated {len(location_counts)} locations with voter counts")
        
    except Exception as e:
        print(f"   ⚠️  Error updating counts: {str(e)}")

def verify_upload(supabase: Client):
    """Verify the uploaded data"""
    print("\n🔍 Verifying upload...")
    
    try:
        # Count locations
        locations = supabase.table('locations').select('*', count='exact').execute()
        locations_count = locations.count if hasattr(locations, 'count') else len(locations.data)
        
        # Count voters
        voters = supabase.table('voters').select('id', count='exact').execute()
        voters_count = voters.count if hasattr(voters, 'count') else len(voters.data)
        
        print(f"\n📊 Upload Summary:")
        print(f"   Locations: {locations_count}")
        print(f"   Voters: {voters_count}")
        
        # Show sample location with voter count
        if locations.data:
            sample = locations.data[0]
            print(f"\n   Sample Location:")
            print(f"   - ID: {sample.get('location_id')}")
            print(f"   - Name: {sample.get('location_name')}")
            print(f"   - Address: {sample.get('location_address')}")
            print(f"   - Total Voters: {sample.get('total_voters')}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error verifying: {str(e)}")
        return False

def main():
    """Main execution function"""
    print("=" * 70)
    print("📤 UPLOAD MOTOBUS DATA TO SUPABASE")
    print("=" * 70)
    
    # Load configuration
    config = load_config()
    print(f"\n📡 Connecting to: {config['url']}")
    
    # Create Supabase client
    supabase: Client = create_client(config['url'], config['key'])
    
    # Load data
    locations_df, voters_df = load_data()
    
    # Upload locations first
    upload_locations(supabase, locations_df)
    
    # Upload voters (linked by location_id)
    upload_voters(supabase, voters_df)
    
    # Update voter counts
    update_location_voter_counts(supabase)
    
    # Verify
    verify_upload(supabase)
    
    print("\n" + "=" * 70)
    print("✅ Upload completed successfully!")
    print("=" * 70)

if __name__ == "__main__":
    main()
