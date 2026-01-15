"""
27_diagnose_duplicates.py - Diagnostic for Script 21 issues

Identifies which districts are missing and which have duplicate extractions.
"""

import pandas as pd
import geopandas as gpd

print("="*70)
print("DIAGNOSTIC: VIIRS Extraction Issues")
print("="*70)

# Load GADM districts (expected)
gadm_gdf = gpd.read_file('01_Data_Raw/District_Boundaries/gadm41_IND_2.shp')
expected_districts = set(gadm_gdf['NAME_2'].unique())
print(f"\n[1] GADM Districts: {len(expected_districts)} unique")

# Load VIIRS monthly panel (actual)
viirs_df = pd.read_csv('02_Data_Intermediate/viirs_monthly_panel.csv')
actual_districts = set(viirs_df['gadm_district'].unique())
print(f"[2] VIIRS Districts: {len(actual_districts)} unique")

# Find missing districts
missing = expected_districts - actual_districts
print(f"\n[3] MISSING DISTRICTS ({len(missing)}):")
if missing:
    for d in sorted(missing):
        print(f"  - {d}")
else:
    print("  (none)")

# Find extra districts (shouldn't happen)
extra = actual_districts - expected_districts
print(f"\n[4] EXTRA DISTRICTS ({len(extra)}):")
if extra:
    for d in sorted(extra):
        print(f"  - {d}")
else:
    print("  (none)")

# Check observation counts per district
obs_per_district = viirs_df.groupby('gadm_district').size()
print(f"\n[5] DISTRICTS WITH ≠ 120 OBSERVATIONS:")
imbalanced = obs_per_district[obs_per_district != 120]
if len(imbalanced) > 0:
    print(imbalanced.sort_values(ascending=False))
else:
    print("  (none)")

# Find the 360-observation district
max_obs_district = obs_per_district.idxmax()
max_obs = obs_per_district.max()
print(f"\n[6] DISTRICT WITH MOST OBS: {max_obs_district} ({max_obs} obs)")

# Sample duplicates for this district
if max_obs > 120:
    print(f"\n[7] Sample data for {max_obs_district}:")
    sample = viirs_df[viirs_df['gadm_district'] == max_obs_district][['gadm_district', 'gadm_state', 'year', 'month']].head(10)
    print(sample)

print("\n" + "="*70)
print("DIAGNOSIS COMPLETE")
print("="*70)
print("\nLikely cause: Script 21 extracted same district multiple times per month")
print("Fix: Check Script 21 logic for duplicate geometries or indexing issue")