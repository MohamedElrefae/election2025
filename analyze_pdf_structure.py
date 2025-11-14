"""
Analyze the PDF structure to understand the exact format
"""
import pdfplumber
import json

def analyze_pdf(pdf_path):
    """Deep analysis of PDF structure"""
    print(f"🔍 Analyzing: {pdf_path}")
    
    with pdfplumber.open(pdf_path) as pdf:
        print(f"\n📖 Total pages: {len(pdf.pages)}")
        
        # Analyze first page in detail
        page = pdf.pages[0]
        
        print("\n" + "=" * 70)
        print("PAGE 1 ANALYSIS")
        print("=" * 70)
        
        # Get raw text
        text = page.extract_text()
        print("\n📝 Raw Text (first 1000 chars):")
        print(text[:1000])
        
        # Get text with layout
        print("\n" + "=" * 70)
        print("TEXT WITH LAYOUT:")
        print("=" * 70)
        text_layout = page.extract_text(layout=True)
        print(text_layout[:1000])
        
        # Try to extract tables
        print("\n" + "=" * 70)
        print("TABLE EXTRACTION:")
        print("=" * 70)
        tables = page.extract_tables()
        if tables:
            print(f"Found {len(tables)} tables")
            for i, table in enumerate(tables[:2]):  # First 2 tables
                print(f"\nTable {i+1}:")
                for row_idx, row in enumerate(table[:10]):  # First 10 rows
                    print(f"  Row {row_idx}: {row}")
        else:
            print("No tables found")
        
        # Get words with positions
        print("\n" + "=" * 70)
        print("WORDS WITH POSITIONS (first 50):")
        print("=" * 70)
        words = page.extract_words()
        for i, word in enumerate(words[:50]):
            print(f"{i}: '{word['text']}' at x={word['x0']:.1f}, y={word['top']:.1f}")
        
        # Analyze page 2 for comparison
        if len(pdf.pages) > 1:
            print("\n" + "=" * 70)
            print("PAGE 2 SAMPLE:")
            print("=" * 70)
            page2 = pdf.pages[1]
            text2 = page2.extract_text()
            print(text2[:500])

def main():
    print("=" * 70)
    print("📄 PDF Structure Analysis")
    print("=" * 70)
    
    analyze_pdf('108.pdf')

if __name__ == "__main__":
    main()
