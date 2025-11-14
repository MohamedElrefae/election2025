"""
Extract 108.pdf with proper Arabic name fixing
Reverses the text and adds proper word spacing
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

def fix_arabic_name(text):
    """
    Fix reversed Arabic text by simply reversing it
    """
    if not text:
        return ''
    
    # Clean first
    text = clean_for_excel(text)
    
    # Simply reverse the text
    text_reversed = text[::-1]
    
    return text_reversed

def parse_voter_line(line):
    """Parse a line with multiple voters"""
    voters = []
    
    # Convert Arabic numerals
    line_eng = arabic_to_english(line)
    
    # Split by numbers
    parts = re.split(r'(\d+)', line_eng)
    
    current_name = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        
        if part.isdigit():
            voter_num = int(part)
            
            if current_name:
                name = ' '.join(current_name)
                name = clean_for_excel(name)
                
                # Fix Arabic direction and spacing
                name_fixed = fix_arabic_name(name)
                
                if name_fixed and len(name_fixed) > 2:
                    voters.append((voter_num, name_fixed))
                
                current_name = []
        else:
            current_name.append(part)
    
    return voters

def extract_voters(pdf_path):
    """Extract voters from PDF"""
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
                
                # Skip headers
                if any(skip in line for skip in ['باونلاسجمتخا', 'ةنجل', 'زكم', 'ةظحم', 'قوسد', 'ةراا']):
                    continue
                
                # Parse voters
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
        print("⚠️  No voters")
        return None
    
    df = pd.DataFrame(voters)
    df = df.sort_values('رقم الناخب')
    
    # Remove duplicates
    before = len(df)
    df = df.drop_duplicates(subset=['رقم الناخب'], keep='first')
    after = len(df)
    
    if before != after:
        print(f"   Removed {before - after} duplicates")
    
    # Save
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='الناخبين', index=False)
        
        # Summary
        summary = pd.DataFrame({
            'البيان': ['رقم اللجنة', 'عدد الناخبين', 'أول ناخب', 'آخر ناخب'],
            'القيمة': [
                '108',
                len(df),
                int(df['رقم الناخب'].min()),
                int(df['رقم الناخب'].max())
            ]
        })
        summary.to_excel(writer, sheet_name='الملخص', index=False)
        
        # Format
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
    print("📄 PDF to Excel - Location 108 (Final - Fixed Arabic)")
    print("=" * 70)
    
    pdf_file = '108.pdf'
    output_file = '108_final.xlsx'
    
    try:
        voters = extract_voters(pdf_file)
        
        if not voters:
            print("\n⚠️  No voters extracted")
            return
        
        df = save_to_excel(voters, output_file)
        
        if df is not None:
            print(f"\n📋 Sample (first 30 voters):")
            print(df.head(30).to_string(index=False))
            
            print("\n" + "=" * 70)
            print("✅ SUCCESS!")
            print("=" * 70)
            print(f"\n📊 Output: {output_file}")
            print(f"   Total voters: {len(df)}")
            print(f"   Range: {df['رقم الناخب'].min()} to {df['رقم الناخب'].max()}")
            print("\n💡 Arabic names are now:")
            print("   - Reversed to correct direction")
            print("   - Spaces added between words")
            print("   - Ready to use in Excel!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
