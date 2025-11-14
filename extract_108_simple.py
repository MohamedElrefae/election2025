"""
Simple PDF to Excel - Extract exactly as is, no processing
"""
import pdfplumber
import pandas as pd
import re

def extract_raw_text_by_page(pdf_path):
    """Extract raw text from each page"""
    print(f"📄 Extracting from: {pdf_path}")
    
    all_data = []
    
    with pdfplumber.open(pdf_path) as pdf:
        print(f"📖 Total pages: {len(pdf.pages)}")
        
        for page_num, page in enumerate(pdf.pages, 1):
            print(f"   Processing page {page_num}/{len(pdf.pages)}...", end='\r')
            
            # Extract text exactly as is
            text = page.extract_text()
            
            if text:
                # Split by lines
                lines = text.split('\n')
                
                for line in lines:
                    # Skip empty lines
                    if not line.strip():
                        continue
                    
                    # Add to data with page number
                    all_data.append({
                        'Page': page_num,
                        'Text': line.strip()
                    })
        
        print(f"\n✅ Extracted {len(all_data)} lines")
    
    return all_data

def clean_for_excel(text):
    """Remove only illegal characters for Excel"""
    if not text:
        return ''
    # Remove control characters that Excel doesn't allow
    text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', str(text))
    return text

def save_raw_to_excel(data, output_file):
    """Save raw data to Excel"""
    print(f"\n💾 Saving to: {output_file}")
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Clean only illegal characters
    df['Text'] = df['Text'].apply(clean_for_excel)
    
    # Save to Excel
    df.to_excel(output_file, index=False, sheet_name='Raw Data')
    
    print(f"✅ Excel file created!")
    print(f"   Rows: {len(df)}")
    print(f"   File: {output_file}")

def main():
    print("=" * 70)
    print("📄 Simple PDF to Excel - Raw Extraction")
    print("=" * 70)
    
    pdf_file = '108.pdf'
    output_file = '108_raw_extraction.xlsx'
    
    try:
        # Extract
        data = extract_raw_text_by_page(pdf_file)
        
        if not data:
            print("⚠️  No data extracted")
            return
        
        # Save
        save_raw_to_excel(data, output_file)
        
        # Show sample
        print(f"\n📋 Sample (first 20 lines):")
        df = pd.DataFrame(data)
        print(df.head(20).to_string(index=False))
        
        print("\n" + "=" * 70)
        print("✅ DONE!")
        print("=" * 70)
        print(f"\n📊 Output: {output_file}")
        print("   Open in Excel and manually format as needed")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
