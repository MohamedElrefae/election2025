"""
Analyze CSV data for duplicates and integrity issues
"""
import pandas as pd

print("=" * 70)
print("CSV DATA ANALYSIS")
print("=" * 70)

# Analyze voters CSV
print("\n📊 VOTERS CSV ANALYSIS")
print("-" * 70)

voters_df = pd.read_csv('motobus voter.csv', sep=';')
print(f"Total rows in CSV: {len(voters_df)}")
print(f"Columns: {list(voters_df.columns)}")

# Clean column names
voters_df.columns = voters_df.columns.str.strip()

# Check voter numbers
print(f"\nVoter Number Statistics:")
print(f"  Unique voter numbers: {voters_df['voter number'].nunique()}")
print(f"  Duplicate voter numbers: {voters_df['voter number'].duplicated().sum()}")

# Convert to numeric for min/max
voters_df['voter_num_clean'] = pd.to_numeric(voters_df['voter number'], errors='coerce')
print(f"  Min voter number: {voters_df['voter_num_clean'].min()}")
print(f"  Max voter number: {voters_df['voter_num_clean'].max()}")

# Check for duplicates
if voters_df['voter number'].duplicated().any():
    print(f"\n⚠️  WARNING: Found duplicate voter numbers!")
    duplicates = voters_df[voters_df['voter number'].duplicated(keep=False)]
    print(f"  Total duplicate records: {len(duplicates)}")
    print(f"\n  Sample duplicates:")
    dup_cols = [col for col in voters_df.columns if col in ['name', 'name ', 'voter number', 'location numer']]
    print(duplicates.head(20)[dup_cols])

# Check location distribution
print(f"\nLocation Distribution:")
location_counts = voters_df['location numer'].value_counts().sort_index()
print(f"  Unique locations: {voters_df['location numer'].nunique()}")
print(f"\n  Top 10 locations by voter count:")
for loc, count in location_counts.head(10).items():
    print(f"    Location {loc}: {count} voters")

# Analyze locations CSV
print("\n" + "=" * 70)
print("📍 LOCATIONS CSV ANALYSIS")
print("-" * 70)

locations_df = pd.read_csv('motobus  locations.csv', sep=';')
print(f"Total rows in CSV: {len(locations_df)}")
print(f"Columns: {list(locations_df.columns)}")

# Clean column names
locations_df.columns = locations_df.columns.str.strip()

print(f"\nLocation Number Statistics:")
print(f"  Unique location numbers: {locations_df['location numer'].nunique()}")
print(f"  Duplicate location numbers: {locations_df['location numer'].duplicated().sum()}")
print(f"  Min location number: {locations_df['location numer'].min()}")
print(f"  Max location number: {locations_df['location numer'].max()}")

# Show all locations
print(f"\nAll Locations:")
for idx, row in locations_df.iterrows():
    print(f"  {row['location numer']}: {row['location name ']}")

# Cross-reference check
print("\n" + "=" * 70)
print("🔍 CROSS-REFERENCE CHECK")
print("-" * 70)

voter_locations = set(voters_df['location numer'].unique())
csv_locations = set(locations_df['location numer'].unique())

print(f"Locations in voters CSV: {len(voter_locations)}")
print(f"Locations in locations CSV: {len(csv_locations)}")

missing_in_locations = voter_locations - csv_locations
if missing_in_locations:
    print(f"\n⚠️  Locations in voters but NOT in locations CSV: {sorted(missing_in_locations)}")

missing_in_voters = csv_locations - voter_locations
if missing_in_voters:
    print(f"\n⚠️  Locations in locations CSV but NOT in voters: {sorted(missing_in_voters)}")

# Sample data
print("\n" + "=" * 70)
print("📋 SAMPLE DATA")
print("-" * 70)

print("\nFirst 10 voters:")
print(voters_df[['name ', 'voter number', 'location numer']].head(10))

print("\nLast 10 voters:")
print(voters_df[['name ', 'voter number', 'location numer']].tail(10))

print("\n" + "=" * 70)
