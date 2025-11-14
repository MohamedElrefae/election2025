"""
Improved extraction for 108.pdf with better text parsing
"""
import pdfplumber
import pandas as pd
import re

def clean_text(text):
    """Clean and normalize text"""
    if not text:
        return ''
    # Remove control characters
    text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    # Remove RTL/LTR marks
    text = re.sub(r'[\u202a-\u202e\u200e\u200f]', '', text)
    # Normalize whitespace
    text = ' '.join(text.split())
    return text.strip()

def arabic_to_english(text):
    """Convert Arabic numerals to English"""
    if not text:
        return text
    arabic = '٠١٢٣٤٥٦٧٨٩'
    english = '0123456789'
    trans = str.maketrans(arabic, english)
    return str(text).translate(trans)

def extract_with_tables(pdf_path):
    """Extract using table detection"""
    print(f"📄 Extracting from: {pdf_path}")
    
    all_voters = []
    location_info = {'number': '108', 'name': '', 'address': ''}
    
    with pdfplumber.open(pdf_path) as pdf:
        print(f"📖 Total pages: {len(pdf.pages)}")
        
        # Try to get location info from first page
        first_page_text = pdf.pages[0].extract_text()
        lines = first_page_text.split('\n')[:15]
        
        for line in lines:
            line = clean_text(line)
            if 'لجنة' in line or 'مدرسة' in line or 'مركز' in line:
                # Extract location number
                nums = re.findall(r'\d+', arabic_to_english(line))
                if nums and not location_info['number']:
                    location_info['number'] = nums[0]
                
                # Store name/address
                if 'مدرسة' in line or 'مركز' in line:
                    if not location_info['name']:
                        location_info['name'] = line
                    elif not location_info['address']:
                        location_info['address'] = line
        
        print(f"📍 Location: {location_info['number']}")
        
        # Process each page
        for page_num, page in enumerate(pdf.pages, 1):
            print(f"   Page {page_num}/{len(pdf.pages)}...", end='\r')
            
            # Try table extraction first
            tables = page.extract_tables()
            
            if tables:
                for table in tables:
                    for row in table:
                        if not row or len(row) < 2:
                            continue
                        
                        # Try to find voter number and name
                        for i, cell in enumerate(row):
                            if not cell:
                                continue
                            
                            cell = clean_text(cell)
                            cell_eng = arabic_to_english(cell)
                            
                            # Check if this looks like a voter number
                            if cell_eng.isdigit() and len(cell_eng) <= 5:
                                voter_num = int(cell_eng)
                                
                                # Get name from next cells
                                name_parts = []
                                for j in range(i+1, len(row)):
                                    if row[j]:
                                        name_parts.append(clean_text(row[j]))
                                
                                if name_parts:
                                    voter_name = ' '.join(name_parts)
                                    
                                    # Validate name
                                    if len(voter_name) > 3 and not voter_name.isdigit():
                                        all_voters.append({
                                            'voter_number': voter_num,
                                            'voter_name': voter_name,
                                            'location_number': location_info['number'],
                                            'page': page_num
                                        })
                                break
            
            # If no tables, try text extraction
            if not tables:
                text = page.extract_text()
                if text:
                    lines = text.split('\n')
                    
                    for line in lines:
                        line = clean_text(line)
                        if not line or len(line) < 5:
                            continue
                        
                        # Pattern: number followed by name
                        parts = line.split()
                        if len(parts) >= 2:
                            first = arabic_to_english(parts[0])
                            
                            if first.isdigit() and len(first) <= 5:
                                voter_num = int(first)
                                voter_name = ' '.join(parts[1:])
                                
                                # Validate
                                if len(voter_name) > 3 and not any(skip in voter_name for skip in ['صفحة', 'لجنة', 'رقم', 'Page']):
                                    all_voters.append({
                                        'voter_number': voter_num,
                                        'voter_name': voter_name,
                                        'location_number': location_info['number'],
                                        'page': page_num
                                    })
    
    print(f"\n✅ Extracted {len(all_voters)} voters")
    return all_voters, location_info

def save_to_excel(voters, location_info, output_file):
    """Save to Excel with proper formatting"""
    print(f"\n💾 Creating Excel file: {output_file}")
    
    if not voters:
        print("⚠️  No voters to save")
        return
    
    # Create DataFrame
    df = pd.DataFrame(voters)
    
    # Sort by voter number
    df = df.sort_values('voter_number')
    
    # Remove duplicates
    df = df.drop_duplicates(subset=['voter_number'], keep='first')
    
    print(f"   Unique voters: {len(df)}")
    
    # Rename columns
    df = df.rename(columns={
        'voter_number': 'رقم الناخب',
        'voter_name': 'اسم الناخب',
        'location_number': 'رقم اللجنة',
        'page': 'رقم الصفحة'
    })
    
    # Create Excel file
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Voters sheet
        df.to_excel(writer, sheet_name='الناخبين', index=False)
        
        # Summary sheet
        summary = pd.DataFrame({
            'البيان': ['رقم اللجنة', 'اسم اللجنة', 'العنوان', 'عدد الناخبين'],
            'القيمة': [
                location_info['number'],
                location_info['name'],
                location_info['address'],
                len(df)
            ]
        })
        summary.to_excel(writer, sheet_name='الملخص', index=False)
        
        # Format columns
        for sheet_name in writer.sheets:
            ws = writer.sheets[sheet_name]
            for column in ws.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if cell.value:
                            max_length = max(max_length, len(str(cell.value)))
                    except:
                        pass
                ws.column_dimensions[column_letter].width = min(max_length + 2, 60)
    
    print(f"✅ Excel file created!")
    return df

def main():
    print("=" * 70)
    print("📄 PDF to Excel - Location 108 (Improved)")
    print("=" * 70)
    
    pdf_file = '108.pdf'
    output_file = '108_voters_extracted.xlsx'
    
    try:
        # Extract
        voters, location_info = extract_with_tables(pdf_file)
        
        if not voters:
            print("\n⚠️  No voters extracted. The PDF might have:")
            print("   - Scanned images instead of text")
            print("   - Unusual formatting")
            print("   - Protected content")
            return
        
        # Save
        df = save_to_excel(voters, location_info, output_file)
        
        # Show sample
        print(f"\n📋 Sample (first 10 voters):")
        print(df.head(10).to_string(index=False))
        
        print("\n" + "=" * 70)
        print("✅ SUCCESS!")
        print("=" * 70)
        print(f"\n📊 Output: {output_file}")
        print(f"   Total voters: {len(df)}")
        print(f"   Location: {location_info['number']}")
        
    except FileNotFoundError:
        print(f"❌ File not found: {pdf_file}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
