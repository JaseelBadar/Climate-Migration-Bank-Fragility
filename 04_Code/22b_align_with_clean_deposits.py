"""
22b_align_with_clean_deposits.py - Align VIIRS with Feb 12 clean deposits
Fixes column names and filters to 624-district analysis sample
"""
import pandas as pd

print("="*70)
print("VIIRS ALIGNMENT - Clean Deposits Sample (624 districts)")
print("="*70)

# Load existing VIIRS quarterly panel (Feb 1, Script 22 output)
print("\n[1] Loading VIIRS quarterly panel...")
viirs_quarterly = pd.read_csv('02_Data_Intermediate/viirs_quarterly_panel.csv')
print(f"    Loaded: {len(viirs_quarterly)} rows")
print(f"    Columns: {list(viirs_quarterly.columns)}")

# Load analysis sample (624 districts, Feb 12 clean deposits)
print("\n[2] Loading analysis sample (clean deposits)...")
master = pd.read_csv('02_Data_Intermediate/master_panel_analysis.csv')
valid_districts = master[['district_gadm', 'state_gadm']].drop_duplicates()
print(f"    Analysis sample districts: {len(valid_districts)}")

# Fix column names
print("\n[3] Fixing column names (gadm_district → district_gadm)...")
viirs_quarterly = viirs_quarterly.rename(columns={
    'gadm_district': 'district_gadm',
    'gadm_state': 'state_gadm'
})
print("    Column names corrected")

# Filter to 624 districts
print("\n[4] Filtering to 624-district sample...")
print(f"    Before: {viirs_quarterly[['district_gadm', 'state_gadm']].drop_duplicates().shape[0]} districts")

viirs_quarterly_clean = viirs_quarterly.merge(
    valid_districts,
    on=['district_gadm', 'state_gadm'],
    how='inner'
)

print(f"    After: {viirs_quarterly_clean[['district_gadm', 'state_gadm']].drop_duplicates().shape[0]} districts")
print(f"    Rows: {len(viirs_quarterly)} -> {len(viirs_quarterly_clean)}")

# Verification: Aurangabad Bihar litmus test
print("\n[5] Verification: Aurangabad Bihar (2020Q1)...")
aur_check = viirs_quarterly_clean[
    (viirs_quarterly_clean['district_gadm'] == 'Aurangabad') & 
    (viirs_quarterly_clean['state_gadm'] == 'Bihar') &
    (viirs_quarterly_clean['year'] == 2020) &
    (viirs_quarterly_clean['q'] == 1)
]

if len(aur_check) > 0:
    print(f"    Aurangabad Bihar 2020Q1 radiance: {aur_check['mean_radiance'].values[0]:.6f}")
    print("    Data integrity verified")
else:
    print("    Aurangabad Bihar not in filtered sample")

# Save
print("\n[6] Saving aligned VIIRS quarterly panel...")
output_path = '02_Data_Intermediate/viirs_quarterly_panel_clean.csv'
viirs_quarterly_clean.to_csv(output_path, index=False)
print(f"    File: {output_path}")
print(f"    Rows: {len(viirs_quarterly_clean)}")

# Summary
print(f"\n[7] SUMMARY")
print(f"    Districts: {viirs_quarterly_clean[['district_gadm', 'state_gadm']].drop_duplicates().shape[0]}")
print(f"    Quarters: {viirs_quarterly_clean['quarter'].nunique()}")
print(f"    Expected rows (624 x 40): {624 * 40}")
print(f"    Actual rows: {len(viirs_quarterly_clean)}")
print(f"    Panel balanced: {len(viirs_quarterly_clean) == 624 * 40}")
print(f"    Mean radiance: {viirs_quarterly_clean['mean_radiance'].mean():.4f}")

print("\n" + "="*70)
print("NEXT STEP: Run Script 23 (merge with master panel)")
print("="*70)