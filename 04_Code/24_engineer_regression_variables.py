"""
24_engineer_regression_variables.py - Phase 3d Variable Engineering

Engineer regression-ready variables per Variables_Codebook_v1.2.md.

VARIABLES CREATED:
  - log_lights_qt (quarterly mean log lights)
  - lights_change_qt (quarter-over-quarter Δ)
  - deposit_change_qt (quarter-over-quarter Δ)
  - Lags: flood_lag1_qt, lights_lag1_qt, deposit_lag1_qt

OUTPUT:
  - 03_Data_Clean/regression_ready_panel.csv

ESTIMATED RUNTIME: 2-3 minutes
"""

import pandas as pd
import numpy as np
import logging
import os

# === SETUP LOGGING ===
os.makedirs('05_Outputs/Logs', exist_ok=True)
logging.basicConfig(
    filename='05_Outputs/Logs/24_variable_engineering.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)

print("="*70)
print("PHASE 3d: Regression Variable Engineering")
print("="*70)
log.info("Starting 24_engineer_regression_variables.py")

# === LOAD ANALYSIS PANEL ===
print(f"\n[1/6] Loading analysis panel...")
df = pd.read_csv('03_Data_Clean/analysis_panel_final.csv')
print(f"  ✓ Loaded: {len(df):,} rows")
print(f"  ✓ Columns: {df.columns.tolist()}")
log.info(f"Analysis panel loaded: {len(df)} rows")

# === SORT BY DISTRICT-QUARTER (Required for lags) ===
print(f"\n[2/6] Sorting by district-quarter...")
df = df.sort_values(['district_gadm', 'state_gadm', 'quarter_num'])
print(f"  ✓ Sorted")
log.info("Panel sorted by district-quarter")

# === LOG TRANSFORMATIONS ===
print(f"\n[3/6] Creating log variables...")

# Log deposits (already exists in master panel as log_deposits_crores)
# We'll keep it; no need to recreate

# Log lights (quarterly mean log)
df['log_lights_qt'] = np.log(df['mean_radiance'] + 1)  # +1 to handle zeros
print(f"  ✓ log_lights_qt created")
log.info("log_lights_qt created")

# === QUARTER-OVER-QUARTER CHANGES ===
print(f"\n[4/6] Computing quarter-over-quarter changes...")

# Group by district
df['deposit_change_qt'] = df.groupby(['district_gadm', 'state_gadm'])['log_deposits_crores'].diff()
df['lights_change_qt'] = df.groupby(['district_gadm', 'state_gadm'])['log_lights_qt'].diff()

print(f"  ✓ deposit_change_qt created")
print(f"  ✓ lights_change_qt created")
log.info("Quarter-over-quarter changes computed")

# === LAGS (L1) ===
print(f"\n[5/6] Creating lag variables...")

df['flood_lag1_qt'] = df.groupby(['district_gadm', 'state_gadm'])['flood_exposure_ruleA_qt'].shift(1)
df['lights_lag1_qt'] = df.groupby(['district_gadm', 'state_gadm'])['log_lights_qt'].shift(1)
df['deposit_lag1_qt'] = df.groupby(['district_gadm', 'state_gadm'])['log_deposits_crores'].shift(1)

print(f"  ✓ flood_lag1_qt created")
print(f"  ✓ lights_lag1_qt created")
print(f"  ✓ deposit_lag1_qt created")
log.info("Lag variables (L1) created")

# === VALIDATION CHECKS ===
print(f"\n[Diagnostics] Variable Validation:")
print(f"  - log_lights_qt: {df['log_lights_qt'].notna().sum():,} non-missing ({df['log_lights_qt'].notna().sum()/len(df)*100:.1f}%)")
print(f"  - lights_change_qt: {df['lights_change_qt'].notna().sum():,} non-missing")
print(f"  - deposit_change_qt: {df['deposit_change_qt'].notna().sum():,} non-missing")
print(f"  - flood_lag1_qt: {df['flood_lag1_qt'].notna().sum():,} non-missing")

# Check for Inf values
inf_check_vars = ['log_lights_qt', 'lights_change_qt', 'deposit_change_qt']
for var in inf_check_vars:
    inf_count = np.isinf(df[var]).sum()
    if inf_count > 0:
        print(f"  ⚠ Warning: {var} has {inf_count} Inf values")
        log.warning(f"{var} has {inf_count} Inf values")

# === SAVE OUTPUT ===
print(f"\n[6/6] Saving regression-ready panel...")
output_path = '03_Data_Clean/regression_ready_panel.csv'
df.to_csv(output_path, index=False)

# === SUMMARY ===
print("="*70)
print("VARIABLE ENGINEERING COMPLETE")
print("="*70)
print(f"Output: {output_path}")
print(f"Total rows: {len(df):,}")
print(f"\nNew variables created:")
print(f"  ✓ log_lights_qt (log mean radiance)")
print(f"  ✓ lights_change_qt (Δ log lights)")
print(f"  ✓ deposit_change_qt (Δ log deposits)")
print(f"  ✓ flood_lag1_qt (L1 flood exposure)")
print(f"  ✓ lights_lag1_qt (L1 log lights)")
print(f"  ✓ deposit_lag1_qt (L1 log deposits)")
print(f"\nSample (first 3 rows with all variables):")
sample_cols = ['district_gadm', 'quarter', 'log_lights_qt', 'lights_change_qt', 'deposit_change_qt']
print(df[sample_cols].dropna(subset=['lights_change_qt']).head(3).to_string(index=False))
log.info(f"Output saved: {output_path}")
print("="*70)
print("\nNEXT STEP: Run Script 25 (descriptive statistics)")
print("="*70)