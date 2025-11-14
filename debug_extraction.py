import pdfplumber
import re

pdf = pdfplumber.open('108.pdf')
table = pdf.pages[0].extract_tables()[0]

print("First 5 rows of table:")
for i, row in enumerate(table[:5]):
    print(f"\nRow {i}:")
    for j, cell in enumerate(row):
        if cell:
            cleaned = cell.replace('\x00', '')
            print(f"  Cell [{j}]: '{cleaned}'")
            
            # Try to extract number
            cell_eng = cleaned
            for a, e in zip('٠١٢٣٤٥٦٧٨٩', '0123456789'):
                cell_eng = cell_eng.replace(a, e)
            
            numbers = re.findall(r'\d+', cell_eng)
            print(f"    Numbers found: {numbers}")
            
            if numbers:
                parts = re.split(r'[٠-٩0-9]+', cleaned)
                print(f"    Name parts: {parts}")
