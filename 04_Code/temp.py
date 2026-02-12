import pandas as pd
df = pd.read_csv('02_Data_Intermediate/master_panel_analysis.csv')

# Check 1: Aurangabad Bihar deposits
aur = df[(df['district_gadm'] == 'Aurangabad') & (df['state_gadm'] == 'Bihar') & (df['quarter'].isin(['2015Q1', '2017Q2', '2023Q1']))]
print("=== AURANGABAD BIHAR CHECK ===")
print(aur[['district_gadm', 'state_gadm', 'quarter', 'deposits']].sort_values('quarter'))

# Check 2: Total counts
print(f"\n=== SAMPLE COUNTS ===")
print(f"Total rows: {len(df)}")
print(f"Unique (district, state) pairs: {df[['district_gadm', 'state_gadm']].drop_duplicates().shape[0]}")
print(f"Unique quarters: {df['quarter'].nunique()}")
print(f"Expected rows (districts × quarters): {df[['district_gadm', 'state_gadm']].drop_duplicates().shape[0] * df['quarter'].nunique()}")

# Check 3: Missing rows diagnostic
print(f"\n=== BALANCE CHECK ===")
print(f"Actual rows: {len(df)}")
print(f"Expected (if balanced): {df[['district_gadm', 'state_gadm']].drop_duplicates().shape[0] * 37}")
print(f"Missing: {(df[['district_gadm', 'state_gadm']].drop_duplicates().shape[0] * 37) - len(df)}")

exit()