"""
23_merge_viirs_master.py - Merge aligned VIIRS quarterly panel with master
panel analysis sample to produce analysis_panel_final.csv
"""
import pandas as pd


print("="*70)
print("PHASE 3d: VIIRS + Master Panel Merge")
print("="*70)


# Load master panel (deposits + floods)
print("\n[1/4] Loading input datasets...")
master_df = pd.read_csv('02_Data_Intermediate/master_panel_analysis.csv')
n_master_districts = master_df.groupby(['district_gadm', 'state_gadm']).ngroups
print(f"    Master panel: {len(master_df):,} rows")
print(f"    Districts:    {n_master_districts} (composite key)")
print(f"    Quarters:     {master_df['quarter'].nunique()}")


# Load VIIRS quarterly panel (aligned with clean deposits, Script 22b)
viirs_df = pd.read_csv('02_Data_Intermediate/viirs_quarterly_panel_clean.csv')
n_viirs_districts = viirs_df.groupby(['district_gadm', 'state_gadm']).ngroups
print(f"    VIIRS panel:  {len(viirs_df):,} rows")
print(f"    Districts:    {n_viirs_districts} (composite key)")
print(f"    Quarters:     {viirs_df['quarter'].nunique()}")


# Verify district alignment
assert n_master_districts == n_viirs_districts, \
    f"District mismatch: master {n_master_districts} vs VIIRS {n_viirs_districts}"
print("    District alignment: confirmed")


# Verify key columns present in both files
print("\n[2/4] Verifying merge keys...")
for col in ['district_gadm', 'state_gadm', 'year', 'quarter']:
    assert col in master_df.columns, f"Missing in master: {col}"
    assert col in viirs_df.columns,  f"Missing in VIIRS: {col}"
print("    Keys present in both files: district_gadm, state_gadm, year, quarter")


# Merge: left join preserves all 23,347 master panel observations
print("\n[3/4] Merging VIIRS with master panel (left join)...")
merged_df = master_df.merge(
    viirs_df[['district_gadm', 'state_gadm', 'year', 'quarter',
              'mean_radiance', 'pixel_count']],
    on=['district_gadm', 'state_gadm', 'year', 'quarter'],
    how='left'
)

assert len(merged_df) == len(master_df), \
    f"Row count changed after merge: {len(master_df):,} -> {len(merged_df):,}"

n_with_viirs   = merged_df['mean_radiance'].notna().sum()
n_missing_viirs = merged_df['mean_radiance'].isna().sum()
coverage_pct   = 100 * n_with_viirs / len(merged_df)

assert n_missing_viirs == 0, \
    f"Missing VIIRS: {n_missing_viirs} observations. Expected 100% coverage."

print(f"    Output rows:     {len(merged_df):,} (row count preserved)")
print(f"    VIIRS coverage:  {n_with_viirs:,} / {len(merged_df):,} ({coverage_pct:.1f}%)")
print(f"    Missing VIIRS:   {n_missing_viirs}")


# Save
print("\n[4/4] Saving final analysis panel...")
output_path = '03_Data_Clean/analysis_panel_final.csv'
merged_df.to_csv(output_path, index=False)
print(f"    File: {output_path}")
print(f"    Rows: {len(merged_df):,}")
print(f"    Columns: {list(merged_df.columns)}")


# Sample
print("\n[Sample] First 3 rows with VIIRS:")
deposit_col = [c for c in merged_df.columns if 'deposit' in c.lower()][0]
print(merged_df[['district_gadm', 'state_gadm', 'quarter',
                  deposit_col, 'mean_radiance']].head(3).to_string(index=False))


print("\n" + "="*70)
print("MERGE COMPLETE")
print("="*70)
print(f"  Output:         {output_path}")
print(f"  Total rows:     {len(merged_df):,}")
print(f"  VIIRS coverage: {coverage_pct:.1f}%")
print(f"  Columns added:  mean_radiance, pixel_count")
print("\n" + "="*70)
print("NEXT STEP: Run Script 24 (engineer regression variables)")
print("="*70)