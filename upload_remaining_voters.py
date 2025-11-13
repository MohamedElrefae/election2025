"""
Upload remaining voters to Supabase with better error handling
"""
import json
import pandas as pd
from supabase import create_client, Client
from tqdm import tqdm
import time

def load_config():
    with open('supabase_config.json', 'r') as f:
        return json.load(f)

def get_uploaded_voter_ids(supabase: Client):
    """Get all voter IDs that are already uploaded"""
    print("📥 Fetching already uploaded voters...")
    
    all_voters = []
    page_size = 1000
    offset = 0
    
    while True:
        response = supabase.table('voters').select('voter_id').range(offset, offset + page_size - 1).execute()
        if not response.data:
            break
        all_voters.extend([v['voter_id'] for v in response.data])
        offset += page_size
        if len(response.data) < page_size:
            break
    
    print(f"   Found {len(all_voters)} already uploaded voters")
    return set(all_voters)

def upload_voters_carefully(supabase: Client, voters_df, uploaded_ids):
    """Upload voters that haven't been uploaded yet"""
    print("\n👥 Preparing voters for upload...")
    
    # Filter out already uploaded voters
    voters_to_upload = voters_df[~voters_df['voter_number'].isin(uploaded_ids)]
    print(f"   Need to upload: {len(voters_to_upload)} voters")
    
    if len(voters_to_upload) == 0:
        print("   ✅ All voters already uploaded!")
        return len(uploaded_ids)
    
    voters_data = []
    for _, row in voters_to_upload.iterrows():
        voters_data.append({
            'voter_id': int(row['voter_number']),
            'full_name': str(row['full_name']).strip(),
            'location_id': int(row['location_number'])
        })
    
    # Upload in small batches with delays
    batch_size = 300
    total_uploaded = len(uploaded_ids)
    failed_count = 0
    
    print("\n📤 Uploading in batches...")
    for i in tqdm(range(0, len(voters_data), batch_size)):
        batch = voters_data[i:i+batch_size]
        
        try:
            supabase.table('voters').insert(batch).execute()
            total_uploaded += len(batch)
            time.sleep(0.5)  # Small delay to avoid rate limits
            
        except Exception as e:
            error_msg = str(e)
            
            # If server error, try smaller batches
            if '500' in error_msg or '502' in error_msg:
                print(f"\n   ⚠️  Server error, trying smaller batches...")
                for j in range(0, len(batch), 50):
                    mini_batch = batch[j:j+50]
                    try:
                        supabase.table('voters').insert(mini_batch).execute()
                        total_uploaded += len(mini_batch)
                        time.sleep(0.3)
                    except Exception as e2:
                        failed_count += len(mini_batch)
                        print(f"   ❌ Failed: {str(e2)[:80]}")
            else:
                failed_count += len(batch)
                print(f"\n   ❌ Batch failed: {error_msg[:100]}")
    
    print(f"\n   ✅ Total uploaded: {total_uploaded}")
    if failed_count > 0:
        print(f"   ⚠️  Failed: {failed_count}")
    
    return total_uploaded

def main():
    print("=" * 70)
    print("📤 UPLOAD REMAINING VOTERS TO SUPABASE")
    print("=" * 70)
    
    config = load_config()
    supabase = create_client(config['url'], config['key'])
    
    # Load voters data
    print("\n📂 Loading voters CSV...")
    voters_df = pd.read_csv('motobus voter.csv', sep=';')
    voters_df = voters_df[['name ', 'voter number', 'location numer']]
    voters_df.columns = ['full_name', 'voter_number', 'location_number']
    voters_df = voters_df.dropna(subset=['voter_number', 'location_number'])
    print(f"   Total voters in CSV: {len(voters_df)}")
    
    # Get already uploaded
    uploaded_ids = get_uploaded_voter_ids(supabase)
    
    # Upload remaining
    total = upload_voters_carefully(supabase, voters_df, uploaded_ids)
    
    print("\n" + "=" * 70)
    print(f"✅ Upload complete! Total voters: {total}")
    print("=" * 70)

if __name__ == "__main__":
    main()
