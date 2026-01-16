import pandas as pd
import numpy as np

print("=" * 70)
print("PHASE 3d: VIIRS + Master Panel Merge")
print("=" * 70)
print()

# ============================================================================
# STEP 1: Load datasets
# ============================================================================
print("[1/4] Loading input datasets...")

# Load master panel (deposits + floods)
master_df = pd.read_csv('02_Data_Intermediate/master_panel_analysis.csv')
print(f"  ✓ Master panel: {len(master_df):,} rows")
print(f"    - Districts: {master_df['district_gadm'].nunique()}")
print(f"    - Quarters: {master_df['quarter'].nunique()}")

# Load VIIRS quarterly panel
viirs_df = pd.read_csv('02_Data_Intermediate/viirs_quarterly_panel.csv')
print(f"  ✓ VIIRS panel: {len(viirs_df):,} rows")
print(f"    - Districts: {viirs_df['gadm_district'].nunique()}")
print(f"    - Quarters: {viirs_df['quarter'].nunique()}")

# ============================================================================
# STEP 2: Standardize column names (CRITICAL!)
# ============================================================================
print()
print("[2/4] Standardizing merge keys...")

# Rename VIIRS columns to match master panel naming
viirs_df = viirs_df.rename(columns={
    'gadm_district': 'district_gadm',
    'gadm_state': 'state_gadm'
})

print("  ✓ Keys standardized")

# ============================================================================
# STEP 3: Merge on district + year + quarter
# ============================================================================
print()
print("[3/4] Merging VIIRS with master panel (left join)...")

# Left join: keep all master panel observations
merged_df = master_df.merge(
    viirs_df[['district_gadm', 'year', 'quarter', 'mean_radiance', 'pixel_count']],
    on=['district_gadm', 'year', 'quarter'],
    how='left',
    suffixes=('', '_viirs')
)

print(f"  ✓ Merge complete")
print(f"  ✓ Output rows: {len(merged_df):,} (same as master)")

# Diagnostics
print()
print("[Diagnostics] VIIRS Coverage:")
n_with_viirs = merged_df['mean_radiance'].notna().sum()
n_missing_viirs = merged_df['mean_radiance'].isna().sum()
print(f"  ✓ Observations with VIIRS: {n_with_viirs:,} / {len(merged_df):,} ({100*n_with_viirs/len(merged_df):.1f}%)")
print(f"  ✓ Observations missing VIIRS: {n_missing_viirs:,}")
print(f"  ✓ Districts with VIIRS: {merged_df[merged_df['mean_radiance'].notna()]['district_gadm'].nunique()} / {merged_df['district_gadm'].nunique()}")

# ============================================================================
# STEP 4: Save final analysis panel
# ============================================================================
print()
print("[4/4] Saving final analysis panel...")

output_path = '03_Data_Clean/analysis_panel_final.csv'
merged_df.to_csv(output_path, index=False)

print("=" * 70)
print("MERGE COMPLETE")
print("=" * 70)
print(f"Output: {output_path}")
print(f"Total rows: {len(merged_df):,}")
print(f"VIIRS coverage: {100*n_with_viirs/len(merged_df):.1f}%")
print()
print("Columns added:")
print("  - mean_radiance (VIIRS quarterly avg)")
print("  - pixel_count (quality diagnostic)")
print()

# Sample output
sample = merged_df[merged_df['mean_radiance'].notna()].head(3)
print("Sample (first 3 rows with VIIRS):")
print(sample[['district_gadm', 'quarter', 'deposits', 'mean_radiance']].to_string(index=False))
print()
print("=" * 70)
print()
print("NEXT STEP: Run Script 24 (engineer regression variables)")
print("=" * 70)