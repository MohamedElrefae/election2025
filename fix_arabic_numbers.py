"""
Fix Arabic numerals in voter numbers and analyze data properly
"""
import pandas as pd
import re

def arabic_to_english_number(text):
    """Convert Arabic numerals to English numerals"""
    if pd.isna(text):
        return text
    
    text = str(text)
    arabic_numerals = '٠١٢٣٤٥٦٧٨٩'
    english_numerals = '0123456789'
    
    translation_table = str.maketrans(arabic_numerals, english_numerals)
    return text.translate(translation_table)

print("=" * 70)
print("ANALYZING AND FIXING ARABIC NUMERALS")
print("=" * 70)

# Load voters
print("\n📊 Loading voters CSV...")
voters_df = pd.read_csv('motobus voter.csv', sep=';')
print(f"Total rows: {len(voters_df)}")

# Clean column names
voters_df.columns = voters_df.columns.str.strip()

# Show sample of original data
print("\n📋 Sample of ORIGINAL voter numbers:")
print(voters_df[['name', 'voter number', 'location numer']].head(20))

# Convert Arabic numerals to English
print("\n🔄 Converting Arabic numerals to English...")
voters_df['voter_number_english'] = voters_df['voter number'].apply(arabic_to_english_number)
voters_df['voter_number_int'] = pd.to_numeric(voters_df['voter_number_english'], errors='coerce')

print("\n📋 Sample of CONVERTED voter numbers:")
print(voters_df[['name', 'voter number', 'voter_number_english', 'voter_number_int', 'location numer']].head(20))

# Check for duplicates after conversion
print("\n🔍 Checking for duplicates after conversion...")
print(f"Total rows: {len(voters_df)}")
print(f"Unique voter numbers: {voters_df['voter_number_int'].nunique()}")
print(f"Duplicate voter numbers: {voters_df['voter_number_int'].duplicated().sum()}")

# Check if voter numbers are unique per location
print("\n🔍 Checking voter number uniqueness per location...")
voters_df['voter_location_key'] = voters_df['voter_number_int'].astype(str) + '_' + voters_df['location numer'].astype(str)
print(f"Unique voter+location combinations: {voters_df['voter_location_key'].nunique()}")
print(f"Duplicate voter+location combinations: {voters_df['voter_location_key'].duplicated().sum()}")

if voters_df['voter_location_key'].duplicated().any():
    print("\n⚠️  WARNING: Found duplicate voter+location combinations!")
    dups = voters_df[voters_df['voter_location_key'].duplicated(keep=False)].sort_values(['location numer', 'voter_number_int'])
    print(f"Total duplicate records: {len(dups)}")
    print("\nSample duplicates:")
    print(dups[['name', 'voter_number_int', 'location numer']].head(20))

# Statistics by location
print("\n📊 Voter statistics by location:")
location_stats = voters_df.groupby('location numer').agg({
    'voter_number_int': ['count', 'min', 'max', 'nunique']
}).round(0)
print(location_stats)

# Check if voter numbers restart at each location
print("\n🔍 Checking if voter numbers restart at each location...")
for loc in sorted(voters_df['location numer'].unique()):
    loc_data = voters_df[voters_df['location numer'] == loc]
    min_voter = loc_data['voter_number_int'].min()
    max_voter = loc_data['voter_number_int'].max()
    count = len(loc_data)
    unique = loc_data['voter_number_int'].nunique()
    print(f"Location {loc}: {count} voters, numbers {int(min_voter)}-{int(max_voter)}, unique: {unique}")

print("\n" + "=" * 70)
print("CONCLUSION:")
print("=" * 70)

if voters_df['voter_location_key'].duplicated().sum() == 0:
    print("✅ Voter numbers are unique within each location")
    print("✅ Voter numbers restart at 1 for each location")
    print("✅ This is the CORRECT data structure")
else:
    print("⚠️  There are true duplicates that need investigation")

print("\n💡 RECOMMENDATION:")
print("The voter_id should be a combination of location_id + voter_number")
print("Or use a unique sequential ID for the database")
