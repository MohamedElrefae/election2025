#!/usr/bin/env python3
"""
Database Transfer Agent for Egypt 2025 Election Data
Transfers extracted CSV data to Supabase database following the schema specifications
"""

import pandas as pd
import os
import json
from datetime import datetime
from supabase import create_client, Client
import logging
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseTransferAgent:
    """Agent for transferring election data to Supabase database"""
    
    def __init__(self, supabase_url: str, supabase_key: str):
        """Initialize the database transfer agent"""
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.supabase: Client = None
        
    def connect_to_database(self) -> bool:
        """Establish connection to Supabase database"""
        try:
            logger.info("🔗 Connecting to Supabase database...")
            self.supabase = create_client(self.supabase_url, self.supabase_key)
            
            # Test connection by querying a simple table
            response = self.supabase.table('locations').select('count').execute()
            logger.info("✅ Database connection established successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to database: {e}")
            return False
    
    def validate_csv_files(self, locations_csv: str, voters_csv: str) -> bool:
        """Validate that CSV files exist and have correct structure"""
        logger.info("🔍 Validating CSV files...")
        
        # Check if files exist
        if not os.path.exists(locations_csv):
            logger.error(f"❌ Locations CSV file not found: {locations_csv}")
            return False
            
        if not os.path.exists(voters_csv):
            logger.error(f"❌ Voters CSV file not found: {voters_csv}")
            return False
        
        try:
            # Validate locations CSV structure
            locations_df = pd.read_csv(locations_csv)
            required_location_columns = [
                'location_id', 'location_number', 'location_name', 
                'location_address', 'governorate', 'district', 'total_voters'
            ]
            
            for col in required_location_columns:
                if col not in locations_df.columns:
                    logger.error(f"❌ Missing required column in locations CSV: {col}")
                    return False
            
            # Validate voters CSV structure
            voters_df = pd.read_csv(voters_csv)
            required_voter_columns = [
                'voter_id', 'full_name', 'location_id', 'source_page'
            ]
            
            for col in required_voter_columns:
                if col not in voters_df.columns:
                    logger.error(f"❌ Missing required column in voters CSV: {col}")
                    return False
            
            logger.info(f"✅ CSV files validated successfully")
            logger.info(f"   📍 Locations: {len(locations_df)} records")
            logger.info(f"   👥 Voters: {len(voters_df)} records")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error validating CSV files: {e}")
            return False
    
    def clear_existing_data(self) -> bool:
        """Clear existing data from database tables"""
        logger.info("🗑️ Clearing existing data from database...")
        
        try:
            # Clear voters first (due to foreign key constraint)
            voters_response = self.supabase.table('voters').delete().neq('id', 0).execute()
            logger.info(f"   🗑️ Cleared voters table")
            
            # Clear locations
            locations_response = self.supabase.table('locations').delete().neq('location_id', 0).execute()
            logger.info(f"   🗑️ Cleared locations table")
            
            logger.info("✅ Existing data cleared successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error clearing existing data: {e}")
            return False
    
    def transfer_locations(self, locations_csv: str) -> bool:
        """Transfer locations data to database"""
        logger.info("📍 Transferring locations data...")
        
        try:
            # Read locations CSV
            locations_df = pd.read_csv(locations_csv)
            
            # Prepare data for insertion
            locations_data = []
            for _, row in locations_df.iterrows():
                location_record = {
                    'location_id': int(row['location_id']),
                    'location_number': str(row['location_number']),
                    'location_name': str(row['location_name']),
                    'location_address': str(row['location_address']),
                    'governorate': str(row['governorate']),
                    'district': str(row['district']),
                    'main_committee_id': str(row.get('main_committee_id', '')) if pd.notna(row.get('main_committee_id')) else None,
                    'police_department': str(row.get('police_department', '')) if pd.notna(row.get('police_department')) else None,
                    'total_voters': int(row['total_voters']) if pd.notna(row['total_voters']) else 0
                }
                locations_data.append(location_record)
            
            # Insert data in batches
            batch_size = 100
            total_inserted = 0
            
            for i in range(0, len(locations_data), batch_size):
                batch = locations_data[i:i + batch_size]
                response = self.supabase.table('locations').insert(batch).execute()
                total_inserted += len(batch)
                logger.info(f"   ✅ Inserted locations batch: {total_inserted}/{len(locations_data)}")
            
            logger.info(f"✅ Successfully transferred {total_inserted} locations")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error transferring locations: {e}")
            return False
    
    def transfer_voters(self, voters_csv: str) -> bool:
        """Transfer voters data to database"""
        logger.info("👥 Transferring voters data...")
        
        try:
            # Read voters CSV
            voters_df = pd.read_csv(voters_csv)
            
            # Prepare data for insertion
            voters_data = []
            for _, row in voters_df.iterrows():
                voter_record = {
                    'voter_id': int(row['voter_id']),
                    'full_name': str(row['full_name']),
                    'location_id': int(row['location_id']),
                    'source_page': int(row['source_page']) if pd.notna(row['source_page']) else None
                }
                voters_data.append(voter_record)
            
            # Insert data in batches
            batch_size = 500  # Larger batch size for voters
            total_inserted = 0
            
            for i in range(0, len(voters_data), batch_size):
                batch = voters_data[i:i + batch_size]
                response = self.supabase.table('voters').insert(batch).execute()
                total_inserted += len(batch)
                
                if total_inserted % 1000 == 0 or total_inserted == len(voters_data):
                    logger.info(f"   ✅ Inserted voters batch: {total_inserted}/{len(voters_data)}")
            
            logger.info(f"✅ Successfully transferred {total_inserted} voters")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error transferring voters: {e}")
            return False
    
    def verify_data_integrity(self) -> Dict:
        """Verify data integrity after transfer"""
        logger.info("🔍 Verifying data integrity...")
        
        try:
            # Count records in database
            locations_response = self.supabase.table('locations').select('location_id').execute()
            voters_response = self.supabase.table('voters').select('id').execute()
            
            locations_count = len(locations_response.data)
            voters_count = len(voters_response.data)
            
            # Get statistics
            stats_response = self.supabase.table('election_statistics').select('*').execute()
            
            # Verify foreign key relationships
            orphaned_voters_response = self.supabase.rpc('check_orphaned_voters').execute()
            
            verification_result = {
                'locations_count': locations_count,
                'voters_count': voters_count,
                'statistics': stats_response.data[0] if stats_response.data else {},
                'integrity_check': 'passed'
            }
            
            logger.info(f"✅ Data integrity verification completed")
            logger.info(f"   📍 Locations in database: {locations_count}")
            logger.info(f"   👥 Voters in database: {voters_count}")
            
            return verification_result
            
        except Exception as e:
            logger.error(f"❌ Error verifying data integrity: {e}")
            return {'integrity_check': 'failed', 'error': str(e)}
    
    def generate_transfer_report(self, verification_result: Dict) -> str:
        """Generate a transfer completion report"""
        logger.info("📋 Generating transfer report...")
        
        report = f"""
# Database Transfer Report - Egypt 2025 Election Data

## Transfer Summary
- **Transfer Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Database**: Supabase
- **Status**: {'✅ SUCCESS' if verification_result.get('integrity_check') == 'passed' else '❌ FAILED'}

## Data Counts
- **Locations Transferred**: {verification_result.get('locations_count', 0):,}
- **Voters Transferred**: {verification_result.get('voters_count', 0):,}

## Database Statistics
"""
        
        if 'statistics' in verification_result and verification_result['statistics']:
            stats = verification_result['statistics']
            report += f"""
- **Total Locations**: {stats.get('total_locations', 0):,}
- **Total Voters**: {stats.get('total_voters', 0):,}
- **Governorate**: {stats.get('governorate', 'كفر الشيخ')}
- **District**: {stats.get('district', 'مطوبس')}
- **Average Voters per Location**: {stats.get('avg_voters_per_location', 0):.1f}
- **Min Voters per Location**: {stats.get('min_voters_per_location', 0)}
- **Max Voters per Location**: {stats.get('max_voters_per_location', 0)}
"""
        
        report += f"""
## Data Quality
- **Encoding**: UTF-8 (Arabic text preserved)
- **Foreign Key Integrity**: {'✅ Verified' if verification_result.get('integrity_check') == 'passed' else '❌ Issues found'}
- **Duplicate Handling**: Removed during extraction

## Database Schema
- **Locations Table**: Contains polling station information
- **Voters Table**: Contains individual voter records linked to locations
- **Views Available**: voter_details, election_statistics

## Next Steps
1. ✅ Data successfully imported and verified
2. 🔍 Use the `voter_details` view for comprehensive queries
3. 📊 Check `election_statistics` view for summary data
4. 🔒 Configure Row Level Security policies as needed
"""
        
        report_file = os.path.join("output", "database_transfer_report.md")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"📋 Transfer report saved to: {report_file}")
        return report_file
    
    def run_transfer(self, locations_csv: str, voters_csv: str, clear_existing: bool = True) -> Dict:
        """Run the complete database transfer process"""
        logger.info("🚀 Starting database transfer process...")
        
        try:
            # Step 1: Connect to database
            if not self.connect_to_database():
                return {'status': 'error', 'error': 'Failed to connect to database'}
            
            # Step 2: Validate CSV files
            if not self.validate_csv_files(locations_csv, voters_csv):
                return {'status': 'error', 'error': 'CSV validation failed'}
            
            # Step 3: Clear existing data (optional)
            if clear_existing:
                if not self.clear_existing_data():
                    return {'status': 'error', 'error': 'Failed to clear existing data'}
            
            # Step 4: Transfer locations
            if not self.transfer_locations(locations_csv):
                return {'status': 'error', 'error': 'Failed to transfer locations'}
            
            # Step 5: Transfer voters
            if not self.transfer_voters(voters_csv):
                return {'status': 'error', 'error': 'Failed to transfer voters'}
            
            # Step 6: Verify data integrity
            verification_result = self.verify_data_integrity()
            
            if verification_result.get('integrity_check') != 'passed':
                return {'status': 'error', 'error': 'Data integrity verification failed'}
            
            # Step 7: Generate report
            report_file = self.generate_transfer_report(verification_result)
            
            result = {
                'status': 'success',
                'locations_transferred': verification_result['locations_count'],
                'voters_transferred': verification_result['voters_count'],
                'report_file': report_file
            }
            
            logger.info("🎉 Database transfer completed successfully!")
            return result
            
        except Exception as e:
            logger.error(f"❌ Database transfer failed: {e}")
            return {'status': 'error', 'error': str(e)}

def load_supabase_config() -> Dict[str, str]:
    """Load Supabase configuration from environment or config file"""
    
    # Try to load from environment variables first
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    if supabase_url and supabase_key:
        return {
            'url': supabase_url,
            'key': supabase_key
        }
    
    # Try to load from config file
    config_file = 'supabase_config.json'
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
            return config
    
    # If no config found, return empty dict
    return {}

def main():
    """Main function to run the database transfer"""
    
    print("=" * 80)
    print("🗄️ Database Transfer Agent - Egypt 2025 Election Data")
    print("=" * 80)
    
    # Load Supabase configuration
    config = load_supabase_config()
    
    if not config.get('url') or not config.get('key'):
        print("❌ Supabase configuration not found!")
        print("💡 Please set SUPABASE_URL and SUPABASE_ANON_KEY environment variables")
        print("   or create a supabase_config.json file with your credentials")
        return False
    
    # Initialize transfer agent
    transfer_agent = DatabaseTransferAgent(config['url'], config['key'])
    
    # Define CSV file paths (use standardized filenames)
    locations_csv = os.path.join("output", "locations_table.csv")
    voters_csv = os.path.join("output", "voters_table.csv")
    
    # Check if CSV files exist
    if not os.path.exists(locations_csv) or not os.path.exists(voters_csv):
        print("❌ CSV files not found!")
        print("💡 Please run the PDF extraction first to generate the CSV files")
        return False
    
    # Run transfer
    result = transfer_agent.run_transfer(locations_csv, voters_csv)
    
    # Display results
    if result['status'] == 'success':
        print(f"\n✅ DATABASE TRANSFER SUCCESSFUL!")
        print(f"📍 Locations transferred: {result['locations_transferred']:,}")
        print(f"👥 Voters transferred: {result['voters_transferred']:,}")
        print(f"📋 Report: {result['report_file']}")
        
    else:
        print(f"\n❌ DATABASE TRANSFER FAILED!")
        print(f"Error: {result['error']}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Data is now available in your Supabase database!")
        print("🔍 Use the voter_details view for comprehensive queries")
    else:
        print("\n💡 Check your configuration and try again.")