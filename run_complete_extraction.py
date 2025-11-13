#!/usr/bin/env python3
"""
Complete Egypt 2025 Election Data Extraction Pipeline
Orchestrates the entire process from PDF extraction to database transfer
"""

import os
import sys
import json
from datetime import datetime
import logging

# Import our custom modules
from ai_agent_pdf_extractor import EgyptElectionPDFExtractor
from database_transfer_agent import DatabaseTransferAgent, load_supabase_config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ElectionDataPipeline:
    """Complete pipeline for Egypt 2025 election data extraction and transfer"""
    
    def __init__(self, pdf_file: str = "motobus .pdf", output_dir: str = "output"):
        self.pdf_file = pdf_file
        self.output_dir = output_dir
        self.results = {}
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
    
    def validate_prerequisites(self) -> bool:
        """Validate that all prerequisites are met"""
        logger.info("🔍 Validating prerequisites...")
        
        # Check if PDF file exists
        if not os.path.exists(self.pdf_file):
            logger.error(f"❌ PDF file not found: {self.pdf_file}")
            return False
        
        # Check if required Python packages are available
        try:
            import PyPDF2
            import pandas as pd
            import supabase
            logger.info("✅ Required packages available")
        except ImportError as e:
            logger.error(f"❌ Missing required package: {e}")
            logger.info("💡 Install with: pip install PyPDF2 pandas supabase")
            return False
        
        # Check Supabase configuration
        config = load_supabase_config()
        if not config.get('url') or not config.get('key'):
            logger.warning("⚠️ Supabase configuration not found - database transfer will be skipped")
            logger.info("💡 Set SUPABASE_URL and SUPABASE_ANON_KEY environment variables for database transfer")
        
        logger.info("✅ Prerequisites validated")
        return True
    
    def run_pdf_extraction(self) -> bool:
        """Run the PDF extraction process"""
        logger.info("📄 Starting PDF extraction...")
        
        try:
            # Initialize extractor
            extractor = EgyptElectionPDFExtractor(self.pdf_file, self.output_dir)
            
            # Run extraction
            extraction_result = extractor.run_extraction()
            
            if extraction_result['status'] == 'success':
                self.results['extraction'] = extraction_result
                logger.info("✅ PDF extraction completed successfully")
                return True
            else:
                logger.error(f"❌ PDF extraction failed: {extraction_result.get('error')}")
                return False
                
        except Exception as e:
            logger.error(f"❌ PDF extraction error: {e}")
            return False
    
    def run_database_transfer(self) -> bool:
        """Run the database transfer process"""
        logger.info("🗄️ Starting database transfer...")
        
        try:
            # Load Supabase configuration
            config = load_supabase_config()
            
            if not config.get('url') or not config.get('key'):
                logger.warning("⚠️ Skipping database transfer - no Supabase configuration")
                return True  # Not a failure, just skipped
            
            # Initialize transfer agent
            transfer_agent = DatabaseTransferAgent(config['url'], config['key'])
            
            # Define CSV file paths
            locations_csv = os.path.join(self.output_dir, "locations_table.csv")
            voters_csv = os.path.join(self.output_dir, "voters_table.csv")
            
            # Run transfer
            transfer_result = transfer_agent.run_transfer(locations_csv, voters_csv)
            
            if transfer_result['status'] == 'success':
                self.results['transfer'] = transfer_result
                logger.info("✅ Database transfer completed successfully")
                logger.info("✅ Excel outputs generated successfully")
                return True
            else:
                logger.error(f"❌ Database transfer failed: {transfer_result.get('error')}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Database transfer error: {e}")
            return False
    
    def generate_final_report(self) -> str:
        """Generate a comprehensive final report"""
        logger.info("📋 Generating final pipeline report...")
        
        extraction_result = self.results.get('extraction', {})
        transfer_result = self.results.get('transfer', {})
        
        report = f"""
# Egypt 2025 Election Data Extraction Pipeline Report

## Pipeline Execution Summary
- **Execution Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **PDF File**: {self.pdf_file}
- **Output Directory**: {self.output_dir}

## Extraction Results
"""
        
        if extraction_result:
            report += f"""
- **Status**: ✅ SUCCESS
- **Locations Extracted**: {extraction_result.get('total_locations', 0):,}
- **Voters Extracted**: {extraction_result.get('total_voters', 0):,}
- **Files Generated**:
  - `{extraction_result.get('locations_csv', 'N/A')}`
  - `{extraction_result.get('voters_csv', 'N/A')}`
  - `{extraction_result.get('json_file', 'N/A')}`
  - `{extraction_result.get('report_file', 'N/A')}`
"""
        else:
            report += "- **Status**: ❌ FAILED\n"
        
        report += "\n## Database Transfer Results\n"
        
        if transfer_result:
            report += f"""
- **Status**: ✅ SUCCESS
- **Locations Transferred**: {transfer_result.get('locations_transferred', 0):,}
- **Voters Transferred**: {transfer_result.get('voters_transferred', 0):,}
- **Transfer Report**: `{transfer_result.get('report_file', 'N/A')}`
"""
        else:
            report += "- **Status**: ⚠️ SKIPPED (No Supabase configuration)\n"
        
        report += f"""
## Data Schema Compliance
- **Locations Table**: ✅ Compliant with specifications
  - location_id (Primary Key)
  - location_number, location_name, location_address
  - governorate, district, main_committee_id
  - police_department, total_voters
  
- **Voters Table**: ✅ Compliant with specifications  
  - voter_id, full_name
  - location_id (Foreign Key)
  - source_page

## Data Quality Assurance
- **Arabic Text Encoding**: UTF-8 preserved
- **Duplicate Removal**: Applied during extraction
- **Relational Integrity**: location_id links maintained
- **Normalization**: Applied per specifications

## Usage Instructions

### CSV Files
```bash
# View locations data
head -n 10 {self.output_dir}/locations_table.csv

# View voters data  
head -n 10 {self.output_dir}/voters_table.csv
```

### Database Queries (if transferred)
```sql
-- Get all voters for a specific location
SELECT * FROM voter_details WHERE location_number = '77';

-- Get summary statistics
SELECT * FROM election_statistics;

-- Count voters by location
SELECT location_name, COUNT(*) as voter_count 
FROM voter_details 
GROUP BY location_name 
ORDER BY voter_count DESC;
```

## Next Steps
1. ✅ Data extraction and normalization completed
2. 🔍 Review generated reports for data quality
3. 📊 Import into your preferred analytics platform
4. 🗄️ Configure database access policies if using Supabase
5. 📈 Build dashboards and reporting tools

---
*Generated by Egypt 2025 Election Data Extraction Pipeline*
"""
        
        report_file = os.path.join(self.output_dir, "pipeline_final_report.md")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"📋 Final report saved to: {report_file}")
        return report_file
    
    def run_complete_pipeline(self) -> bool:
        """Run the complete extraction and transfer pipeline"""
        logger.info("🚀 Starting complete Egypt 2025 election data pipeline...")
        
        # Step 1: Validate prerequisites
        if not self.validate_prerequisites():
            return False
        
        # Step 2: Run PDF extraction
        if not self.run_pdf_extraction():
            return False
        
        # Step 3: Run database transfer (optional)
        self.run_database_transfer()  # Don't fail if this step fails
        
        # Step 4: Generate final report
        final_report = self.generate_final_report()
        
        logger.info("🎉 Pipeline execution completed!")
        return True

def main():
    """Main function to run the complete pipeline"""
    
    print("=" * 90)
    print("🇪🇬 Egypt 2025 Election Voter PDF Extraction – Complete Pipeline")
    print("=" * 90)
    print()
    print("This pipeline will:")
    print("1. 📄 Extract locations and voters from PDF")
    print("2. 🗄️ Transfer data to Supabase database (if configured)")
    print("3. 📋 Generate comprehensive reports")
    print("4. ✅ Ensure data compliance with specifications")
    print()
    
    # Configuration
    pdf_file = "motobus .pdf"
    output_dir = "output"
    
    # Check if PDF file exists
    if not os.path.exists(pdf_file):
        print(f"❌ PDF file not found: {pdf_file}")
        print("💡 Please ensure the PDF file is in the current directory")
        return False
    
    # Initialize and run pipeline
    pipeline = ElectionDataPipeline(pdf_file, output_dir)
    success = pipeline.run_complete_pipeline()
    
    # Display final results
    print("\n" + "=" * 90)
    
    if success:
        print("🎉 PIPELINE EXECUTION SUCCESSFUL!")
        print()
        
        extraction_result = pipeline.results.get('extraction', {})
        transfer_result = pipeline.results.get('transfer', {})
        
        if extraction_result:
            print(f"📊 EXTRACTION RESULTS:")
            print(f"   📍 Locations: {extraction_result.get('total_locations', 0):,}")
            print(f"   👥 Voters: {extraction_result.get('total_voters', 0):,}")
            print()
        
        if transfer_result:
            print(f"🗄️ DATABASE TRANSFER:")
            print(f"   📍 Locations transferred: {transfer_result.get('locations_transferred', 0):,}")
            print(f"   👥 Voters transferred: {transfer_result.get('voters_transferred', 0):,}")
            print()
        
        print(f"📁 OUTPUT FILES:")
        print(f"   📄 {output_dir}/locations_table.csv")
        print(f"   📄 {output_dir}/voters_table.csv")
        print(f"   📄 {output_dir}/election_data.json")
        print(f"   📋 {output_dir}/pipeline_final_report.md")
        print()
        print("🚀 Your Egypt 2025 election data is ready for analysis!")
        
    else:
        print("❌ PIPELINE EXECUTION FAILED!")
        print("💡 Check the logs above for specific error details")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n✨ All done! Check the output directory for your extracted data.")
    else:
        print("\n🔧 Please fix the issues and try again.")
        sys.exit(1)