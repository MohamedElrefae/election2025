"""
Extract data from 108.pdf and convert to Excel
"""
import pdfplumber
import pandas as pd
import re

def clean_arabic_text(text):
    """Clean Arabic text"""
    if not text:
        return ''
    # Remove control characters and illegal characters
    text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text.strip()

def arabic_to_english_number(text):
    """Convert Arabic numerals to English"""
    if not text:
        return text
    text = str(text)
    arabic_numerals = '٠١٢٣٤٥٦٧٨٩'
    english_numerals = '0123456789'
    translation_table = str.maketrans(arabic_numerals, english_numerals)
    return text.translate(translation_table)

def extract_location_info(pdf_path):
    """Extract location information from first page"""
    with pdfplumber.open(pdf_path) as pdf:
        first_page = pdf.pages[0]
        text = first_page.extract_text()
        
        # Try to find location number and name
        lines = text.split('\n')
        location_number = None
        location_name = None
        location_address = None
        
        for i, line in enumerate(lines[:10]):  # Check first 10 lines
            # Look for location number pattern
            if 'لجنة' in line or 'رقم' in line:
                # Extract number
                numbers = re.findall(r'\d+', arabic_to_english_number(line))
                if numbers:
                    location_number = numbers[0]
            
            # Look for location name/address
            if any(keyword in line for keyword in ['مدرسة', 'مركز', 'قرية', 'عزبة']):
                if not location_name:
                    location_name = clean_arabic_text(line)
                elif not location_address:
                    location_address = clean_arabic_text(line)
        
        return location_number, location_name, location_address

def extract_voters_from_pdf(pdf_path):
    """Extract voter data from PDF"""
    print(f"📄 Processing: {pdf_path}")
    
    # Get location info
    location_number, location_name, location_address = extract_location_info(pdf_path)
    print(f"📍 Location: {location_number} - {location_name}")
    
    voters = []
    
    with pdfplumber.open(pdf_path) as pdf:
        print(f"📖 Total pages: {len(pdf.pages)}")
        
        for page_num, page in enumerate(pdf.pages, 1):
            print(f"   Processing page {page_num}/{len(pdf.pages)}...", end='\r')
            
            # Extract text
            text = page.extract_text()
            if not text:
                continue
            
            lines = text.split('\n')
            
            for line in lines:
                line = clean_arabic_text(line)
                if not line:
                    continue
                
                # Try to extract voter number and name
                # Pattern: number followed by name
                parts = line.split()
                
                if len(parts) >= 2:
                    # Check if first part is a number (in Arabic or English)
                    first_part = arabic_to_english_number(parts[0])
                    
                    if first_part.isdigit():
                        voter_number = int(first_part)
                        voter_name = ' '.join(parts[1:])
                        
                        # Clean the name
                        voter_name = clean_arabic_text(voter_name)
                        
                        # Skip if name is too short or looks like header
                        if len(voter_name) > 3 and not any(skip in voter_name for skip in ['صفحة', 'لجنة', 'رقم']):
                            voters.append({
                                'voter_number': voter_number,
                                'voter_name': voter_name,
                                'location_number': location_number or '108',
                                'location_name': location_name or '',
                                'location_address': location_address or '',
                                'page': page_num
                            })
        
        print(f"\n✅ Extracted {len(voters)} voters")
    
    return voters, location_number, location_name, location_address

def save_to_excel(voters, location_info, output_file):
    """Save voters to Excel file"""
    print(f"\n💾 Saving to Excel: {output_file}")
    
    # Create DataFrame
    df = pd.DataFrame(voters)
    
    # Reorder columns
    columns_order = ['voter_number', 'voter_name', 'location_number', 'location_name', 'location_address', 'page']
    df = df[columns_order]
    
    # Rename columns to Arabic
    df.columns = ['رقم الناخب', 'اسم الناخب', 'رقم اللجنة', 'اسم اللجنة', 'عنوان اللجنة', 'رقم الصفحة']
    
    # Create Excel writer
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Write voters data
        df.to_excel(writer, sheet_name='الناخبين', index=False)
        
        # Create summary sheet
        summary_data = {
            'البيان': ['رقم اللجنة', 'اسم اللجنة', 'العنوان', 'إجمالي الناخبين'],
            'القيمة': [
                location_info[0] or '108',
                location_info[1] or '',
                location_info[2] or '',
                len(voters)
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='الملخص', index=False)
        
        # Auto-adjust column widths
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
    
    print(f"✅ Excel file created successfully!")
    print(f"   File: {output_file}")
    print(f"   Sheets: الناخبين (voters), الملخص (summary)")
    print(f"   Total voters: {len(voters)}")

def main():
    print("=" * 70)
    print("📄 PDF to Excel Converter - Location 108")
    print("=" * 70)
    
    pdf_file = '108.pdf'
    output_file = '108_voters.xlsx'
    
    try:
        # Extract voters
        voters, loc_num, loc_name, loc_addr = extract_voters_from_pdf(pdf_file)
        
        if not voters:
            print("⚠️  No voters found in PDF")
            return
        
        # Save to Excel
        save_to_excel(voters, (loc_num, loc_name, loc_addr), output_file)
        
        # Show sample
        print(f"\n📋 Sample data (first 10 voters):")
        df_sample = pd.DataFrame(voters[:10])
        print(df_sample[['voter_number', 'voter_name']].to_string(index=False))
        
        print("\n" + "=" * 70)
        print("✅ Conversion completed successfully!")
        print("=" * 70)
        print(f"\n📊 Output file: {output_file}")
        print(f"   Open in Excel to view the data")
        
    except FileNotFoundError:
        print(f"❌ Error: File '{pdf_file}' not found")
        print("   Make sure 108.pdf is in the current directory")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
