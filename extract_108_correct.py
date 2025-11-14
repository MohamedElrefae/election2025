"""
Correct extraction for 108.pdf - Parse the actual format
The PDF has format: "name3 number3 name2 number2 name1 number1" on each line
"""
import pdfplumber
import pandas as pd
import re

def arabic_to_english(text):
    """Convert Arabic numerals to English"""
    if not text:
        return text
    arabic = '٠١٢٣٤٥٦٧٨٩'
    english = '0123456789'
    trans = str.maketrans(arabic, english)
    return str(text).translate(trans)

def clean_for_excel(text):
    """Remove illegal characters"""
    if not text:
        return ''
    text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', str(text))
    return text.strip()

def parse_voter_line(line):
    """
    Parse a line that contains multiple voters in format:
    "name3 number3 name2 number2 name1 number1"
    Returns list of (number, name) tuples
    """
    voters = []
    
    # Convert Arabic numerals
    line_eng = arabic_to_english(line)
    
    # Find all numbers in the line
    # Pattern: find sequences of digits
    parts = re.split(r'(\d+)', line_eng)
    
    # Process parts
    current_name = []
    for i, part in enumerate(parts):
        part = part.strip()
        if not part:
            continue
        
        if part.isdigit():
            # This is a voter number
            voter_num = int(part)
            
            # Get the name (text before this number)
            if current_name:
                name = ' '.join(current_name)
                name = clean_for_excel(name)
                
                if name and len(name) > 2:
                    voters.append((voter_num, name))
                
                current_name = []
        else:
            # This is part of a name
            current_name.append(part)
    
    # Handle any remaining name
    if current_name:
        name = ' '.join(current_name)
        name = clean_for_excel(name)
        if name and len(name) > 2:
            # This might be a name without a number, skip it
            pass
    
    return voters

def extract_voters_properly(pdf_path):
    """Extract voters with proper parsing"""
    print(f"📄 Extracting from: {pdf_path}")
    
    all_voters = []
    location_number = '108'
    
    with pdfplumber.open(pdf_path) as pdf:
        print(f"📖 Total pages: {len(pdf.pages)}")
        
        for page_num, page in enumerate(pdf.pages, 1):
            print(f"   Page {page_num}/{len(pdf.pages)}...", end='\r')
            
            text = page.extract_text()
            if not text:
                continue
            
            lines = text.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Skip header lines
                if any(skip in line for skip in ['باونلاسجمتخا', 'ةنجل', 'زكم', 'ةظحم', 'قوسد']):
                    continue
                
                # Parse voters from this line
                voters = parse_voter_line(line)
                
                for voter_num, voter_name in voters:
                    all_voters.append({
                        'رقم الناخب': voter_num,
                        'اسم الناخب': voter_name,
                        'رقم اللجنة': location_number,
                        'رقم الصفحة': page_num
                    })
        
        print(f"\n✅ Extracted {len(all_voters)} voters")
    
    return all_voters

def save_to_excel(voters, output_file):
    """Save to Excel"""
    print(f"\n💾 Creating Excel: {output_file}")
    
    if not voters:
        print("⚠️  No voters to save")
        return None
    
    # Create DataFrame
    df = pd.DataFrame(voters)
    
    # Sort by voter number
    df = df.sort_values('رقم الناخب')
    
    # Remove duplicates
    before = len(df)
    df = df.drop_duplicates(subset=['رقم الناخب'], keep='first')
    after = len(df)
    
    if before != after:
        print(f"   Removed {before - after} duplicates")
    
    # Save to Excel
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='الناخبين', index=False)
        
        # Summary
        summary = pd.DataFrame({
            'البيان': ['رقم اللجنة', 'عدد الناخبين', 'أول ناخب', 'آخر ناخب'],
            'القيمة': [
                '108',
                len(df),
                df['رقم الناخب'].min(),
                df['رقم الناخب'].max()
            ]
        })
        summary.to_excel(writer, sheet_name='الملخص', index=False)
        
        # Format columns
        for sheet_name in writer.sheets:
            ws = writer.sheets[sheet_name]
            for column in ws.columns:
                max_length = 0
                col_letter = column[0].column_letter
                for cell in column:
                    try:
                        if cell.value:
                            max_length = max(max_length, len(str(cell.value)))
                    except:
                        pass
                ws.column_dimensions[col_letter].width = min(max_length + 2, 60)
    
    print(f"✅ Excel created!")
    return df

def main():
    print("=" * 70)
    print("📄 PDF to Excel - Location 108 (Correct Parser)")
    print("=" * 70)
    
    pdf_file = '108.pdf'
    output_file = '108_correct.xlsx'
    
    try:
        # Extract
        voters = extract_voters_properly(pdf_file)
        
        if not voters:
            print("\n⚠️  No voters extracted")
            print("   The PDF might be in a different format")
            return
        
        # Save
        df = save_to_excel(voters, output_file)
        
        if df is not None:
            # Show sample
            print(f"\n📋 Sample (first 20 voters):")
            print(df.head(20).to_string(index=False))
            
            print("\n" + "=" * 70)
            print("✅ SUCCESS!")
            print("=" * 70)
            print(f"\n📊 Output: {output_file}")
            print(f"   Total voters: {len(df)}")
            print(f"   Voter numbers: {df['رقم الناخب'].min()} to {df['رقم الناخب'].max()}")
        
    except FileNotFoundError:
        print(f"❌ File not found: {pdf_file}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
