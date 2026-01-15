"""
22_aggregate_viirs_quarterly.py - Phase 3d VIIRS Integration

Aggregate monthly VIIRS to quarterly level (align with master panel structure).

INPUT:
  - 02_Data_Intermediate/viirs_monthly_panel.csv

OUTPUT:
  - 02_Data_Intermediate/viirs_quarterly_panel.csv
  - Expected: 27,040 rows (676 districts × 40 quarters)

ESTIMATED RUNTIME: 1-2 minutes
"""

import pandas as pd
import numpy as np
import logging
import os

# === SETUP LOGGING ===
os.makedirs('05_Outputs/Logs', exist_ok=True)
logging.basicConfig(
    filename='05_Outputs/Logs/22_viirs_quarterly.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)

print("="*70)
print("PHASE 3d: VIIRS Quarterly Aggregation")
print("="*70)
log.info("Starting 22_aggregate_viirs_quarterly.py")

# === LOAD MONTHLY PANEL ===
print(f"\n[1/4] Loading monthly VIIRS panel...")
monthly_df = pd.read_csv('02_Data_Intermediate/viirs_monthly_panel.csv')
print(f"  ✓ Loaded: {len(monthly_df):,} rows")
print(f"  ✓ Districts: {monthly_df['gadm_district'].nunique()}")
print(f"  ✓ Months: {monthly_df[['year', 'month']].drop_duplicates().shape[0]}")
log.info(f"Monthly panel loaded: {len(monthly_df)} rows")

# === MAP MONTHS TO QUARTERS ===
print(f"\n[2/4] Mapping months to quarters...")

def month_to_quarter(month):
    """Map month (1-12) to quarter (1-4)"""
    if month in [1, 2, 3]:
        return 1
    elif month in [4, 5, 6]:
        return 2
    elif month in [7, 8, 9]:
        return 3
    else:  # [10, 11, 12]
        return 4

monthly_df['q'] = monthly_df['month'].apply(month_to_quarter)
monthly_df['quarter'] = monthly_df['year'].astype(str) + 'Q' + monthly_df['q'].astype(str)

print(f"  ✓ Quarters created")
print(f"  ✓ Sample: {monthly_df[['year', 'month', 'quarter']].head(3).to_string(index=False)}")
log.info("Month-to-quarter mapping complete")

# === AGGREGATE TO QUARTERLY ===
print(f"\n[3/4] Aggregating to quarterly level...")

# Group by district, state, year, quarter
quarterly_df = monthly_df.groupby(
    ['gadm_district', 'gadm_state', 'year', 'quarter', 'q'],
    as_index=False
).agg({
    'mean_radiance': 'mean',     # Average radiance across 3 months in quarter
    'pixel_count': 'sum'         # Total pixels processed in quarter
})

print(f"  ✓ Quarterly records: {len(quarterly_df):,}")
print(f"  ✓ Districts: {quarterly_df['gadm_district'].nunique()}")
print(f"  ✓ Quarters: {quarterly_df['quarter'].nunique()}")
log.info(f"Quarterly aggregation complete: {len(quarterly_df)} rows")

# === SAVE OUTPUT ===
print(f"\n[4/4] Saving quarterly panel...")
output_path = '02_Data_Intermediate/viirs_quarterly_panel.csv'
quarterly_df.to_csv(output_path, index=False)

# === SUMMARY ===
print("="*70)
print("AGGREGATION COMPLETE")
print("="*70)
print(f"Output: {output_path}")
print(f"Total rows: {len(quarterly_df):,}")
print(f"Expected: {676 * 40:,} (676 districts × 40 quarters)")
print(f"Coverage: {len(quarterly_df) / (676 * 40) * 100:.1f}%")
print(f"\nSample (first 3 rows):")
print(quarterly_df[['gadm_district', 'gadm_state', 'quarter', 'mean_radiance']].head(3).to_string(index=False))
log.info(f"Output saved: {output_path}")
print("="*70)
print("\nNEXT STEP: Run Script 23 (merge with master panel)")
print("="*70)