"""
20_aggregate_viirs_to_quarterly.py - Phase 3d VIIRS Integration
Aggregate monthly VIIRS to quarterly level and test merge with master panel
Test with Jan 2023 only before processing all 120 tiles
"""
import pandas as pd
import numpy as np
import logging
import os

# Setup logging
os.makedirs('05_Outputs/Logs', exist_ok=True)
logging.basicConfig(
    filename='05_Outputs/Logs/20_viirs_quarterly_test.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)

print("="*70)
print("PHASE 3d: VIIRS Quarterly Aggregation (Test)")
print("="*70)

# === STEP 1: Load VIIRS test data ===
print(f"\n[1/5] Loading VIIRS Jan 2023 test data...")
viirs_df = pd.read_csv('02_Data_Intermediate/viirs_jan2023_test.csv')
print(f"   Loaded: {len(viirs_df)} districts")
print(f"   Columns: {list(viirs_df.columns)}")

# === STEP 2: Map month to quarter ===
print(f"\n[2/5] Mapping months to quarters...")
def month_to_quarter(month):
    """Map month (1-12) to quarter (Q1-Q4)"""
    if month in [1, 2, 3]:
        return 'Q1'
    elif month in [4, 5, 6]:
        return 'Q2'
    elif month in [7, 8, 9]:
        return 'Q3'
    else:
        return 'Q4'

viirs_df['quarter'] = viirs_df['month'].apply(month_to_quarter)
print(f"   Jan 2023 mapped to: {viirs_df['quarter'].iloc[0]}")

# === STEP 3: Aggregate to quarterly (for multi-month data in future) ===
print(f"\n[3/5] Aggregating to quarterly level...")
# Group by district, state, year, quarter
viirs_quarterly = viirs_df.groupby(['gadm_district', 'gadm_state', 'year', 'quarter']).agg({
    'mean_radiance': 'mean',  # Average radiance across months in quarter
    'pixel_count': 'sum'       # Total pixels processed
}).reset_index()

print(f"   Quarterly records: {len(viirs_quarterly)}")
print(f"   Sample (first 3 rows):")
print(viirs_quarterly.head(3))

# === STEP 4: Test merge with master panel ===
print(f"\n[4/5] Testing merge with master panel...")
master_df = pd.read_csv('02_Data_Intermediate/master_panel_analysis.csv')
print(f"   Master panel: {len(master_df)} district-quarters")

# Check master panel 'q' column format
print(f"   Master 'q' dtype: {master_df['q'].dtype}")
print(f"   Master 'q' sample: {list(master_df['q'].unique()[:5])}")

# Rename VIIRS columns to match master panel
viirs_quarterly.rename(columns={
    'gadm_district': 'district_gadm',
    'gadm_state': 'state_gadm'
}, inplace=True)

# Convert VIIRS quarter format to match master panel
if master_df['q'].dtype == 'object':
    # Master uses string format (Q1, Q2, etc.)
    viirs_quarterly.rename(columns={'quarter': 'q'}, inplace=True)
    print(f"   Using string format for 'q': Q1, Q2, etc.")
else:
    # Master uses numeric format (1, 2, 3, 4)
    quarter_map = {'Q1': 1, 'Q2': 2, 'Q3': 3, 'Q4': 4}
    viirs_quarterly['q'] = viirs_quarterly['quarter'].map(quarter_map)
    viirs_quarterly.drop(columns=['quarter'], inplace=True)
    print(f"   Converted to numeric format: 1, 2, 3, 4")

print(f"   VIIRS 'q' dtype after conversion: {viirs_quarterly['q'].dtype}")
print(f"   VIIRS 'q' sample: {list(viirs_quarterly['q'].unique())}")

# Merge on district, state, year, quarter
merged_df = master_df.merge(
    viirs_quarterly[['district_gadm', 'state_gadm', 'year', 'q', 'mean_radiance', 'pixel_count']],
    on=['district_gadm', 'state_gadm', 'year', 'q'],
    how='left',
    indicator=True
)

# Check merge statistics
merge_stats = merged_df['_merge'].value_counts()
print(f"\n   Merge statistics:")
print(f"      Matched (both): {merge_stats.get('both', 0)}")
print(f"      Master only (no VIIRS): {merge_stats.get('left_only', 0)}")
print(f"      VIIRS only (no master): {merge_stats.get('right_only', 0)}")

# Calculate coverage
total_obs = len(merged_df)
viirs_coverage = (merge_stats.get('both', 0) / total_obs) * 100
print(f"\n   VIIRS coverage: {viirs_coverage:.2f}% ({merge_stats.get('both', 0)}/{total_obs} obs)")

# === STEP 5: Save test merge ===
print(f"\n[5/5] Saving test merge output...")

# Drop merge indicator
merged_df.drop(columns=['_merge'], inplace=True)

# Save
output_path = '02_Data_Intermediate/master_panel_viirs_test.csv'
merged_df.to_csv(output_path, index=False)
print(f"   Saved: {output_path}")

# Summary statistics
print("\n" + "="*70)
print("MERGE TEST SUMMARY")
print("="*70)
print(f"Total observations: {len(merged_df)}")
print(f"Observations with VIIRS data: {merged_df['mean_radiance'].notna().sum()}")
print(f"VIIRS coverage: {viirs_coverage:.2f}%")
print(f"\nVIIRS radiance statistics (where available):")
viirs_subset = merged_df[merged_df['mean_radiance'].notna()]
if len(viirs_subset) > 0:
    print(f"  Mean: {viirs_subset['mean_radiance'].mean():.4f}")
    print(f"  Median: {viirs_subset['mean_radiance'].median():.4f}")
    print(f"  Min: {viirs_subset['mean_radiance'].min():.4f}")
    print(f"  Max: {viirs_subset['mean_radiance'].max():.4f}")
else:
    print("  No VIIRS data matched")

# Decision logic
if viirs_coverage < 10.0:
    print(f"\n⚠ WARNING: Only {viirs_coverage:.2f}% coverage (Jan 2023 only)")
    print("   This is EXPECTED for test tile")
    print("   Need to download remaining 119 tiles for full coverage")
    print("\nNEXT STEP: Download all VIIRS tiles (2015-2024)")
    print("   Estimated: 120 tiles × 2GB = 240 GB total")
else:
    print(f"\n✓ Good coverage: {viirs_coverage:.2f}%")
    
print("="*70)

# Log results
log.info(f"Test merge complete: {viirs_coverage:.2f}% coverage")
log.info(f"Total obs: {len(merged_df)}, VIIRS obs: {merged_df['mean_radiance'].notna().sum()}")

print("\nDone. Output saved to 02_Data_Intermediate/master_panel_viirs_test.csv")