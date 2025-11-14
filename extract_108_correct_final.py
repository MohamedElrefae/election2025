"""
Correct extraction for 108.pdf
Table structure: [name1, num1, name2, num2, name3, num3]
"""
import pdfplumber
import pandas as pd

def clean_text(text):
    if not text:
        return ''
    return text.replace('\x00', '').strip()

def arabic_to_english(text):
    if not text:
        return text
    for a, e in zip('٠١٢٣٤٥٦٧٨٩', '0123456789'):
        text = text.replace(a, e)
    return text

def reverse_arabic(text):
    """Reverse Arabic text to fix direction"""
    return text[::-1]

print("Extracting from 108.pdf...")

all_voters = []

with pdfplumber.open('108.pdf') as pdf:
    print(f"Total pages: {len(pdf.pages)}")
    
    for page_num, page in enumerate(pdf.pages, 1):
        tables = page.extract_tables()
        
        if not tables:
            continue
        
        for table in tables:
            for row in table[1:]:  # Skip header row
                if not row or len(row) < 6:
                    continue
                
                # Process 3 voters per row (columns 0-1, 2-3, 4-5)
                for i in range(0, 6, 2):
                    if i+1 < len(row):
                        name = clean_text(row[i])
                        number = clean_text(row[i+1])
                        
                        if name and number:
                            # Convert number
                            number_eng = arabic_to_english(number)
                            if number_eng.isdigit():
                                # Reverse name to fix Arabic direction
                                name_fixed = reverse_arabic(name)
                                
                                all_voters.append({
                                    'رقم الناخب': int(number_eng),
                                    'اسم الناخب': name_fixed,
                                    'رقم اللجنة': '108',
                                    'رقم الصفحة': page_num
                                })

print(f"Extracted: {len(all_voters)} voters")

# Create DataFrame
df = pd.DataFrame(all_voters)
df = df.sort_values('رقم الناخب')
df = df.drop_duplicates(subset=['رقم الناخب'], keep='first')

print(f"Unique voters: {len(df)}")

# Save to Excel
output_file = '108_correct_final.xlsx'

with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name='الناخبين', index=False)
    
    # Summary
    summary = pd.DataFrame({
        'البيان': ['رقم اللجنة', 'عدد الناخبين', 'أول ناخب', 'آخر ناخب'],
        'القيمة': ['108', len(df), int(df['رقم الناخب'].min()), int(df['رقم الناخب'].max())]
    })
    summary.to_excel(writer, sheet_name='الملخص', index=False)

print(f"\nSaved to: {output_file}")
print("\nSample (first 30 voters):")
print(df.head(30).to_string(index=False))

print("\n" + "=" * 70)
print("SUCCESS! Arabic names are reversed to correct direction.")
print("=" * 70)
