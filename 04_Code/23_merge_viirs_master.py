"""
23_merge_viirs_master.py - Phase 3d VIIRS Integration

Merge VIIRS quarterly with master analysis panel (deposits + floods).

INPUT:
  - 02_Data_Intermediate/viirs_quarterly_panel.csv
  - 02_Data_Intermediate/master_panel_analysis.csv

OUTPUT:
  - 03_Data_Clean/analysis_panel_final.csv
  - Expected coverage: ~90%+ (vs 2.70% from test merge)

ESTIMATED RUNTIME: < 1 minute
"""

import pandas as pd
import logging
import os

# === SETUP LOGGING ===
os.makedirs('05_Outputs/Logs', exist_ok=True)
logging.basicConfig(
    filename='05_Outputs/Logs/23_viirs_master_merge.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)

print("="*70)
print("PHASE 3d: VIIRS + Master Panel Merge")
print("="*70)
log.info("Starting 23_merge_viirs_master.py")

# === LOAD INPUTS ===
print(f"\n[1/4] Loading input datasets...")

# Master panel (deposits + floods)
master_df = pd.read_csv('02_Data_Intermediate/master_panel_analysis.csv')
print(f"  ✓ Master panel: {len(master_df):,} rows")
print(f"    - Districts: {master_df['district_gadm'].nunique()}")
print(f"    - Quarters: {master_df['quarter'].nunique()}")
log.info(f"Master panel loaded: {len(master_df)} rows")

# VIIRS quarterly
viirs_df = pd.read_csv('02_Data_Intermediate/viirs_quarterly_panel.csv')
print(f"  ✓ VIIRS panel: {len(viirs_df):,} rows")
print(f"    - Districts: {viirs_df['gadm_district'].nunique()}")
print(f"    - Quarters: {viirs_df['quarter'].nunique()}")
log.info(f"VIIRS panel loaded: {len(viirs_df)} rows")

# === STANDARDIZE MERGE KEYS ===
print(f"\n[2/4] Standardizing merge keys...")

# Master panel uses: district_gadm, state_gadm, quarter
# VIIRS uses: gadm_district, gadm_state, quarter
# We'll merge on: district + state + quarter (triple key for safety)

viirs_df_renamed = viirs_df.rename(columns={
    'gadm_district': 'district_gadm',
    'gadm_state': 'state_gadm'
})

print(f"  ✓ Keys standardized")
log.info("Merge keys standardized")

# === MERGE (LEFT JOIN) ===
print(f"\n[3/4] Merging VIIRS with master panel (left join)...")

merged_df = master_df.merge(
    viirs_df_renamed[['district_gadm', 'state_gadm', 'quarter', 'mean_radiance', 'pixel_count']],
    on=['district_gadm', 'state_gadm', 'quarter'],
    how='left'
)

print(f"  ✓ Merge complete")
print(f"  ✓ Output rows: {len(merged_df):,} (same as master)")
log.info(f"Merge complete: {len(merged_df)} rows")

# === COVERAGE DIAGNOSTICS ===
print(f"\n[Diagnostics] VIIRS Coverage:")
viirs_coverage = merged_df['mean_radiance'].notna().sum()
viirs_coverage_pct = (viirs_coverage / len(merged_df)) * 100

print(f"  ✓ Observations with VIIRS: {viirs_coverage:,} / {len(merged_df):,} ({viirs_coverage_pct:.1f}%)")
print(f"  ✓ Observations missing VIIRS: {merged_df['mean_radiance'].isna().sum():,}")
log.info(f"VIIRS coverage: {viirs_coverage_pct:.1f}%")

# Districts with VIIRS data
districts_with_viirs = merged_df[merged_df['mean_radiance'].notna()]['district_gadm'].nunique()
total_districts = merged_df['district_gadm'].nunique()
print(f"  ✓ Districts with VIIRS: {districts_with_viirs} / {total_districts}")

# === SAVE OUTPUT ===
print(f"\n[4/4] Saving final analysis panel...")
os.makedirs('03_Data_Clean', exist_ok=True)
output_path = '03_Data_Clean/analysis_panel_final.csv'
merged_df.to_csv(output_path, index=False)

# === SUMMARY ===
print("="*70)
print("MERGE COMPLETE")
print("="*70)
print(f"Output: {output_path}")
print(f"Total rows: {len(merged_df):,}")
print(f"VIIRS coverage: {viirs_coverage_pct:.1f}%")
print(f"\nColumns added:")
print(f"  - mean_radiance (VIIRS quarterly avg)")
print(f"  - pixel_count (quality diagnostic)")
print(f"\nSample (first 3 rows with VIIRS):")
sample = merged_df[merged_df['mean_radiance'].notna()].head(3)
print(sample[['district_gadm', 'quarter', 'deposits_crores', 'mean_radiance']].to_string(index=False))
log.info(f"Output saved: {output_path} ({viirs_coverage_pct:.1f}% VIIRS coverage)")
print("="*70)
print("\nNEXT STEP: Run Script 24 (engineer regression variables)")
print("="*70)