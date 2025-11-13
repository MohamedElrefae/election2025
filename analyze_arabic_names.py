"""
Analyze Arabic name structure to determine best splitting strategy
"""
import pandas as pd
from collections import Counter

print("=" * 70)
print("ARABIC NAME STRUCTURE ANALYSIS")
print("=" * 70)

# Load voters
voters_df = pd.read_csv('motobus voter.csv', sep=';')
voters_df.columns = voters_df.columns.str.strip()

print(f"\nTotal voters: {len(voters_df)}")

# Sample names
print("\n📋 Sample Names (first 30):")
for i, name in enumerate(voters_df['name'].head(30), 1):
    parts = str(name).strip().split()
    print(f"{i:2d}. {name}")
    print(f"    Parts: {len(parts)} - {parts}")

# Analyze name structure
print("\n📊 Name Structure Statistics:")
name_lengths = voters_df['name'].apply(lambda x: len(str(x).strip().split()))
print(f"\nName part counts:")
for length, count in sorted(Counter(name_lengths).items()):
    print(f"  {length} parts: {count:,} names ({count/len(voters_df)*100:.1f}%)")

# Common patterns
print("\n🔍 Common Name Patterns:")
print("\nArabic names typically follow these patterns:")
print("  1. [First Name] [Father's Name] [Grandfather's Name] [Family Name]")
print("  2. [First Name] [Father's Name] [Family Name]")
print("  3. [First Name] [Family Name]")

# Analyze last words (potential family names)
print("\n👨‍👩‍👧‍👦 Most Common Last Names (Family Names):")
last_names = voters_df['name'].apply(lambda x: str(x).strip().split()[-1] if pd.notna(x) else '')
last_name_counts = Counter(last_names).most_common(20)
for name, count in last_name_counts:
    print(f"  {name}: {count:,} occurrences")

# Analyze first words (first names)
print("\n👤 Most Common First Names:")
first_names = voters_df['name'].apply(lambda x: str(x).strip().split()[0] if pd.notna(x) else '')
first_name_counts = Counter(first_names).most_common(20)
for name, count in first_name_counts:
    print(f"  {name}: {count:,} occurrences")

print("\n" + "=" * 70)
print("RECOMMENDATION:")
print("=" * 70)
print("""
For Arabic names, the best approach is:
1. FIRST NAME: First word of the full name
2. FAMILY NAME: Last word of the full name
3. MIDDLE NAMES: Everything between first and last (optional)

This allows grouping by family while preserving the full name structure.
""")
