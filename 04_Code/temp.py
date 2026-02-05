import pandas as pd

df = pd.read_csv('02_Data_Intermediate/master_panel_raw.csv')

print("="*70)
print("MASTER PANEL RAW - VALIDATION")
print("="*70)
print(f"Total rows: {len(df):,}")
print(f"Districts: {df['district_gadm'].nunique()}")
print(f"Quarters: {df['quarter'].nunique()}")  # Changed from 'quarter_str'
print(f"\nColumns: {df.columns.tolist()}")

print(f"\nNon-null deposits: {df['deposits'].notna().sum():,}")  # Changed from 'deposits_crores'
print(f"\nDeposit statistics (Crores):")
print(df['deposits'].describe())

# Check 2022Q4 median (critical test)
q4_2022 = df[(df['year']==2022) & (df['q']==4)]['deposits'].median()
print(f"\n2022Q4 median: {q4_2022:,.0f} Crores")
print("✓ PASS if ~7,800-8,000 Crores")
print("✗ FAIL if 162 Crores (would indicate contamination still present)")