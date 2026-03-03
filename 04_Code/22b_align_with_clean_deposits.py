"""
22b_align_with_clean_deposits.py - Align VIIRS with Feb 12 clean deposits
Fixes column names, normalizes case, and filters to analysis-sample districts
"""
import pandas as pd


print("="*70)
print("VIIRS ALIGNMENT - Clean Deposits Sample")
print("="*70)


# Load existing VIIRS quarterly panel (Script 22 output)
print("\n[1] Loading VIIRS quarterly panel...")
viirs_quarterly = pd.read_csv('02_Data_Intermediate/viirs_quarterly_panel.csv')
print(f"    Loaded: {len(viirs_quarterly)} rows")
print(f"    Columns: {list(viirs_quarterly.columns)}")


# Load analysis sample (clean deposits)
print("\n[2] Loading analysis sample (clean deposits)...")
master = pd.read_csv('02_Data_Intermediate/master_panel_analysis.csv')
valid_districts = master[['district_gadm', 'state_gadm']].drop_duplicates()
valid_districts['district_gadm'] = valid_districts['district_gadm'].str.strip()
valid_districts['state_gadm']    = valid_districts['state_gadm'].str.strip()
print(f"    Analysis sample districts: {len(valid_districts)}")


# Fix column names
print("\n[3] Fixing column names (gadm_district -> district_gadm)...")
viirs_quarterly = viirs_quarterly.rename(columns={
    'gadm_district': 'district_gadm',
    'gadm_state':    'state_gadm'
})
print("    Column names corrected")


# Normalize case: VIIRS is Title Case, master panel is UPPERCASE
print("\n[3b] Normalizing case (Title Case -> UPPERCASE to match master panel)...")
viirs_quarterly['district_gadm'] = viirs_quarterly['district_gadm'].str.upper().str.strip()
viirs_quarterly['state_gadm']    = viirs_quarterly['state_gadm'].str.upper().str.strip()
print("    Case normalized")


# Filter to analysis-sample districts
print("\n[4] Filtering to analysis-sample districts...")
n_before = viirs_quarterly.groupby(['district_gadm', 'state_gadm']).ngroups
print(f"    Before: {n_before} districts")

viirs_quarterly_clean = viirs_quarterly.merge(
    valid_districts,
    on=['district_gadm', 'state_gadm'],
    how='inner'
)

n_after    = viirs_quarterly_clean.groupby(['district_gadm', 'state_gadm']).ngroups
n_quarters = viirs_quarterly_clean['quarter'].nunique()
expected   = n_after * n_quarters

print(f"    After: {n_after} districts")
print(f"    Rows: {len(viirs_quarterly)} -> {len(viirs_quarterly_clean)}")

assert len(viirs_quarterly_clean) == expected, \
    f"Unbalanced output: {len(viirs_quarterly_clean)} rows != {n_after} x {n_quarters}"


# Verification: Aurangabad Bihar litmus test
print("\n[5] Verification: Aurangabad Bihar (2020Q1)...")
aur_check = viirs_quarterly_clean[
    (viirs_quarterly_clean['district_gadm'] == 'AURANGABAD') &
    (viirs_quarterly_clean['state_gadm']    == 'BIHAR')      &
    (viirs_quarterly_clean['year']          == 2020)         &
    (viirs_quarterly_clean['q']             == 1)
]

if len(aur_check) > 0:
    print(f"    Aurangabad Bihar 2020Q1 radiance: {aur_check['mean_radiance'].values[0]:.6f}")
    print("    Data integrity verified")
else:
    print("    WARNING: Aurangabad Bihar not in filtered sample")


# Save
print("\n[6] Saving aligned VIIRS quarterly panel...")
output_path = '02_Data_Intermediate/viirs_quarterly_panel_clean.csv'
viirs_quarterly_clean.to_csv(output_path, index=False)
print(f"    File: {output_path}")
print(f"    Rows: {len(viirs_quarterly_clean)}")


# Summary
print(f"\n[7] SUMMARY")
print(f"    Districts: {n_after}")
print(f"    Quarters:  {n_quarters}")
print(f"    Expected rows ({n_after} x {n_quarters}): {expected}")
print(f"    Actual rows:   {len(viirs_quarterly_clean)}")
print(f"    Panel balanced: {len(viirs_quarterly_clean) == expected}")
print(f"    Mean radiance:  {viirs_quarterly_clean['mean_radiance'].mean():.4f}")


print("\n" + "="*70)
print("NEXT STEP: Run Script 23 (merge with master panel)")
print("="*70)