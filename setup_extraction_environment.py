#!/usr/bin/env python3
"""
Setup script for Egypt 2025 Election PDF Extraction environment
Installs dependencies and configures the environment
"""

import subprocess
import sys
import os
import json
from pathlib import Path

def install_requirements():
    """Install required Python packages"""
    print("📦 Installing required Python packages...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements_extraction.txt"
        ])
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def create_output_directory():
    """Create output directory structure"""
    print("📁 Creating output directory structure...")
    
    directories = [
        "output",
        "output/logs",
        "output/reports"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ Created: {directory}")
    
    return True

def create_sample_config():
    """Create sample Supabase configuration file"""
    print("⚙️ Creating sample configuration files...")
    
    # Sample Supabase config
    sample_config = {
        "url": "https://your-project.supabase.co",
        "key": "your-anon-key-here",
        "note": "Replace with your actual Supabase URL and anon key"
    }
    
    config_file = "supabase_config.json.sample"
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(sample_config, f, indent=2)
    
    print(f"   ✅ Created: {config_file}")
    
    # Create environment variables template
    env_template = """# Egypt 2025 Election Data Extraction Environment Variables
# Copy this to .env and fill in your actual values

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here

# Optional: Logging level
LOG_LEVEL=INFO

# Optional: Output directory
OUTPUT_DIR=output
"""
    
    with open(".env.template", 'w', encoding='utf-8') as f:
        f.write(env_template)
    
    print(f"   ✅ Created: .env.template")
    
    return True

def verify_pdf_file():
    """Check if the PDF file exists"""
    print("📄 Checking for PDF file...")
    
    pdf_file = "motobus .pdf"
    
    if os.path.exists(pdf_file):
        print(f"   ✅ Found PDF file: {pdf_file}")
        
        # Get file size
        file_size = os.path.getsize(pdf_file)
        print(f"   📊 File size: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)")
        
        return True
    else:
        print(f"   ⚠️ PDF file not found: {pdf_file}")
        print("   💡 Please ensure the PDF file is in the current directory")
        return False

def create_run_scripts():
    """Create convenient run scripts"""
    print("🚀 Creating run scripts...")
    
    # Windows batch script
    batch_script = """@echo off
echo Egypt 2025 Election PDF Extraction
echo ===================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Run the extraction pipeline
echo Starting extraction pipeline...
python run_complete_extraction.py

echo.
echo Extraction completed. Check the output directory for results.
pause
"""
    
    with open("run_extraction.bat", 'w', encoding='utf-8') as f:
        f.write(batch_script)
    
    print(f"   ✅ Created: run_extraction.bat")
    
    # PowerShell script
    ps_script = """# Egypt 2025 Election PDF Extraction - PowerShell Script

Write-Host "Egypt 2025 Election PDF Extraction" -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Green
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python version: $pythonVersion" -ForegroundColor Blue
} catch {
    Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Run the extraction pipeline
Write-Host "Starting extraction pipeline..." -ForegroundColor Yellow
python run_complete_extraction.py

Write-Host ""
Write-Host "Extraction completed. Check the output directory for results." -ForegroundColor Green
Read-Host "Press Enter to exit"
"""
    
    with open("run_extraction.ps1", 'w', encoding='utf-8') as f:
        f.write(ps_script)
    
    print(f"   ✅ Created: run_extraction.ps1")
    
    return True

def create_readme():
    """Create comprehensive README file"""
    print("📋 Creating README file...")
    
    readme_content = """# Egypt 2025 Election PDF Extraction

AI Agent for extracting structured voter data from Egyptian election PDFs and transferring to Supabase database.

## Features

- 📄 **PDF Text Extraction**: Extracts text from scanned/digital Egyptian election PDFs
- 🏫 **Location Detection**: Identifies polling stations/committees with Arabic names and addresses
- 👥 **Voter Extraction**: Extracts individual voter names linked to locations
- 🗄️ **Database Transfer**: Transfers data to Supabase with proper schema
- 📊 **Data Validation**: Ensures data integrity and compliance with specifications
- 📋 **Comprehensive Reporting**: Generates detailed extraction and transfer reports

## Quick Start

### 1. Setup Environment

```bash
# Install dependencies
python setup_extraction_environment.py

# Or manually install requirements
pip install -r requirements_extraction.txt
```

### 2. Configure Database (Optional)

Create `supabase_config.json`:
```json
{
  "url": "https://your-project.supabase.co",
  "key": "your-anon-key-here"
}
```

Or set environment variables:
```bash
set SUPABASE_URL=https://your-project.supabase.co
set SUPABASE_ANON_KEY=your-anon-key-here
```

### 3. Run Extraction

```bash
# Complete pipeline (extraction + database transfer)
python run_complete_extraction.py

# Or use the batch script
run_extraction.bat
```

## Output Files

- `output/locations_table.csv` - Polling station information
- `output/voters_table.csv` - Individual voter records
- `output/election_data.json` - Complete dataset in JSON format
- `output/pipeline_final_report.md` - Comprehensive extraction report

## Database Schema

### Locations Table
| Field | Type | Description |
|-------|------|-------------|
| location_id | int | Unique identifier |
| location_number | string | Sub-committee number |
| location_name | string | School/location name in Arabic |
| location_address | string | Full address in Arabic |
| governorate | string | Governorate (كفر الشيخ) |
| district | string | District (مطوبس) |
| main_committee_id | string | Main committee number |
| police_department | string | Associated police department |
| total_voters | int | Number of voters at location |

### Voters Table
| Field | Type | Description |
|-------|------|-------------|
| voter_id | int | Voter sequence number |
| full_name | string | Complete Arabic name |
| location_id | int | Foreign key to locations |
| source_page | int | PDF page number |

## Data Quality Features

- ✅ **UTF-8 Encoding**: Preserves Arabic text with diacritics
- ✅ **Duplicate Removal**: Eliminates duplicate entries
- ✅ **Relational Integrity**: Maintains foreign key relationships
- ✅ **Data Validation**: Validates Arabic names and location data
- ✅ **Error Handling**: Comprehensive error reporting and recovery

## Troubleshooting

### Common Issues

1. **PDF Not Found**
   - Ensure `motobus .pdf` is in the current directory
   - Check file name spelling (note the space in filename)

2. **Database Connection Failed**
   - Verify Supabase URL and key are correct
   - Check internet connection
   - Ensure Supabase project is active

3. **No Data Extracted**
   - PDF might be image-based (requires OCR)
   - Check PDF structure in `output/raw_pdf_text.txt`
   - Adjust extraction patterns if needed

### Getting Help

1. Check the generated reports in `output/` directory
2. Review log messages for specific error details
3. Examine `output/raw_pdf_text.txt` to understand PDF structure

## Advanced Usage

### Custom PDF Processing

```python
from ai_agent_pdf_extractor import EgyptElectionPDFExtractor

# Initialize with custom settings
extractor = EgyptElectionPDFExtractor("custom.pdf", "custom_output")

# Run extraction
result = extractor.run_extraction()
```

### Database Queries

```sql
-- Get all voters for a specific location
SELECT * FROM voter_details WHERE location_number = '77';

-- Summary statistics
SELECT * FROM election_statistics;

-- Voters by governorate
SELECT governorate, COUNT(*) as total_voters 
FROM voter_details 
GROUP BY governorate;
```

## Requirements

- Python 3.7+
- PyPDF2 for PDF processing
- pandas for data manipulation
- supabase-py for database connectivity

## License

This project is designed for Egyptian election data processing and should be used in compliance with local data protection and election laws.
"""
    
    with open("README.md", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"   ✅ Created: README.md")
    
    return True

def main():
    """Main setup function"""
    print("=" * 70)
    print("🇪🇬 Egypt 2025 Election PDF Extraction - Environment Setup")
    print("=" * 70)
    print()
    
    success = True
    
    # Step 1: Install requirements
    if not install_requirements():
        success = False
    
    print()
    
    # Step 2: Create directories
    create_output_directory()
    print()
    
    # Step 3: Create configuration files
    create_sample_config()
    print()
    
    # Step 4: Check PDF file
    verify_pdf_file()
    print()
    
    # Step 5: Create run scripts
    create_run_scripts()
    print()
    
    # Step 6: Create README
    create_readme()
    print()
    
    # Final summary
    print("=" * 70)
    
    if success:
        print("🎉 SETUP COMPLETED SUCCESSFULLY!")
        print()
        print("📋 Next Steps:")
        print("1. 📄 Ensure 'motobus .pdf' is in the current directory")
        print("2. ⚙️ Configure Supabase credentials (optional):")
        print("   - Copy supabase_config.json.sample to supabase_config.json")
        print("   - Fill in your actual Supabase URL and key")
        print("3. 🚀 Run the extraction:")
        print("   - Double-click run_extraction.bat")
        print("   - Or run: python run_complete_extraction.py")
        print()
        print("📁 Check the 'output' directory for results!")
        
    else:
        print("❌ SETUP ENCOUNTERED ISSUES!")
        print("💡 Please resolve the errors above and try again")
    
    return success

if __name__ == "__main__":
    success = main()
    
    if not success:
        input("\nPress Enter to exit...")
        sys.exit(1)