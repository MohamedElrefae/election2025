"""
Export Location 108 from motobus voter.csv to Excel
This uses the already-correct data from the CSV file
"""
import pandas as pd

def arabic_to_english(text):
    """Convert Arabic numerals to English"""
    if pd.isna(text):
        return text
    text = str(text)
    arabic = '٠١٢٣٤٥٦٧٨٩'
    english = '0123456789'
    trans = str.maketrans(arabic, english)
    return text.translate(trans)

def main():
    print("=" * 70)
    print("📄 Export Location 108 from CSV to Excel")
    print("=" * 70)
    
    # Load CSV
    print("\n📂 Loading motobus voter.csv...")
    df = pd.read_csv('motobus voter.csv', sep=';')
    df.columns = df.columns.str.strip()
    
    print(f"   Total voters in CSV: {len(df):,}")
    
    # Filter location 108
    print("\n🔍 Filtering location 108...")
    loc108 = df[df['location numer'] == 108].copy()
    
    print(f"   Location 108 voters: {len(loc108):,}")
    
    # Clean and prepare data
    loc108 = loc108[['name', 'voter number', 'location numer']].copy()
    
    # Convert Arabic numerals in voter numbers
    loc108['voter_number_english'] = loc108['voter number'].apply(arabic_to_english)
    loc108['voter_number_int'] = pd.to_numeric(loc108['voter_number_english'], errors='coerce')
    
    # Sort by voter number
    loc108 = loc108.sort_values('voter_number_int')
    
    # Prepare final DataFrame
    final_df = pd.DataFrame({
        'رقم الناخب': loc108['voter_number_int'].astype(int),
        'اسم الناخب': loc108['name'],
        'رقم اللجنة': loc108['location numer']
    })
    
    # Save to Excel
    output_file = '108_from_csv.xlsx'
    print(f"\n💾 Saving to Excel: {output_file}")
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Main data
        final_df.to_excel(writer, sheet_name='الناخبين', index=False)
        
        # Summary
        summary = pd.DataFrame({
            'البيان': [
                'رقم اللجنة',
                'عدد الناخبين',
                'أول ناخب',
                'آخر ناخب'
            ],
            'القيمة': [
                108,
                len(final_df),
                int(final_df['رقم الناخب'].min()),
                int(final_df['رقم الناخب'].max())
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
    
    print(f"✅ Excel file created!")
    
    # Show sample
    print(f"\n📋 Sample (first 20 voters):")
    print(final_df.head(20).to_string(index=False))
    
    print("\n" + "=" * 70)
    print("✅ SUCCESS!")
    print("=" * 70)
    print(f"\n📊 Output: {output_file}")
    print(f"   Total voters: {len(final_df):,}")
    print(f"   Voter range: {final_df['رقم الناخب'].min()} to {final_df['رقم الناخب'].max()}")
    print("\n💡 Names are properly formatted in Arabic!")
    print("   This data comes from the verified CSV file.")

if __name__ == "__main__":
    main()
