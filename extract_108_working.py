import pdfplumber
import pandas as pd
import re

def clean_text(text):
    if not text:
        return ''
    text = str(text).replace('\x00', '')
    text = re.sub(r'[\x01-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    return text.strip()

def arabic_to_english(text):
    if not text:
        return text
    arabic = '٠١٢٣٤٥٦٧٨٩'
    english = '0123456789'
    return str(text).translate(str.maketrans(arabic, english))

def extract_voter(cell_text):
    if not cell_text:
        return None, None
    
    cell_text = clean_text(cell_text)
    if len(cell_text) < 2:
        return None, None
    
    cell_eng = arabic_to_english(cell_text)
    numbers = re.findall(r'\d+', cell_eng)
    
    if not numbers:
        return None, None
    
    voter_num = int(numbers[-1])
    parts = re.split(r'[٠-٩0-9]+', cell_text)
    name = max(parts, key=len).strip() if parts else ''
    
    if name and len(name) > 2:
        return voter_num, name
    
    return None, None

print("Starting extraction...")

all_voters = []
location = '108'

with pdfplumber.open('108.pdf') as pdf:
    print(f"Pages: {len(pdf.pages)}")
    
    for page_num, page in enumerate(pdf.pages, 1):
        tables = page.extract_tables()
        
        if tables:
            for table in tables:
                for row in table:
                    if row:
                        for cell in row:
                            if cell:
                                num, name = extract_voter(cell)
                                if num and name:
                                    all_voters.append({
                                        'voter_number': num,
                                        'voter_name': name,
                                        'location': location,
                                        'page': page_num
                                    })

print(f"Extracted: {len(all_voters)} voters")

df = pd.DataFrame(all_voters)
df = df.sort_values('voter_number')
df = df.drop_duplicates(subset=['voter_number'], keep='first')

print(f"Unique: {len(df)} voters")
print("\nSample:")
print(df.head(20))

df.to_excel('108_working.xlsx', index=False)
print("\nSaved to: 108_working.xlsx")
