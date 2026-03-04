"""
24_engineer_regression_variables.py
Engineer log transforms, quarter-over-quarter changes, and distributed
lag variables from analysis_panel_final.csv. Output: regression_panel_final.csv
"""
import pandas as pd
import numpy as np


print("=" * 70)
print("PHASE 3d: Regression Variable Engineering")
print("=" * 70)
print()


# ============================================================================
# STEP 1: Load analysis panel
# ============================================================================
print("[1/6] Loading analysis panel...")
df = pd.read_csv('03_Data_Clean/analysis_panel_final.csv')
print(f"  Loaded: {len(df):,} rows")
print(f"  Columns: {df.columns.tolist()}")
assert len(df) == 23347, f"Expected 23,347 rows, got {len(df):,}"
print()


# ============================================================================
# STEP 2: Sort by district-quarter (critical for time-series operations)
# ============================================================================
print("[2/6] Sorting by district-quarter...")
df = df.sort_values(['district_gadm', 'state_gadm', 'year', 'q']).reset_index(drop=True)
n_districts = df.groupby(['district_gadm', 'state_gadm']).ngroups
print(f"  Sorted -- {n_districts} districts (composite key)")
print()


# ============================================================================
# STEP 3: Create log variables (for elasticities)
# ============================================================================
print("[3/6] Creating log variables...")

# Log of deposits (Rs Crores) -- +1 offset, deposits always > 0 but safe default
df['log_deposits'] = np.log(df['deposits'] + 1)

# Log of nighttime lights (nW/cm2/sr)
# +0.001 offset per Codebook v1.8: preserves log-scale compression for low-radiance
# districts where mean_radiance << 1. Using +1 would linearise the transform for
# ~80% of the sample (rural/semi-urban districts with radiance < 1).
df['log_lights_qt'] = np.log(df['mean_radiance'] + 0.001)

print(f"  log_deposits:  min={df['log_deposits'].min():.4f}, "
      f"max={df['log_deposits'].max():.4f}, "
      f"mean={df['log_deposits'].mean():.4f}")
print(f"  log_lights_qt: min={df['log_lights_qt'].min():.4f}, "
      f"max={df['log_lights_qt'].max():.4f}, "
      f"mean={df['log_lights_qt'].mean():.4f}")
print()


# ============================================================================
# STEP 4: Create quarter-over-quarter changes (log first differences)
# ============================================================================
print("[4/6] Computing quarter-over-quarter changes...")

df['deposit_change_qt'] = df.groupby(['district_gadm', 'state_gadm'])['log_deposits'].diff()
df['lights_change_qt']  = df.groupby(['district_gadm', 'state_gadm'])['log_lights_qt'].diff()

print(f"  deposit_change_qt -- missing (expected 631): {df['deposit_change_qt'].isna().sum():,}")
print(f"  lights_change_qt  -- missing (expected 631): {df['lights_change_qt'].isna().sum():,}")
print()


# ============================================================================
# STEP 5: Create lagged flood variables (for distributed lag models)
# ============================================================================
print("[5/6] Creating lagged flood exposure variables...")

for lag in range(1, 5):
    df[f'flood_ruleA_L{lag}'] = (
        df.groupby(['district_gadm', 'state_gadm'])['flood_exposure_ruleA_qt'].shift(lag)
    )
    df[f'flood_ruleB_L{lag}'] = (
        df.groupby(['district_gadm', 'state_gadm'])['flood_exposure_ruleB_qt'].shift(lag)
    )

print("  Lags L1-L4 created for Rule A and Rule B")
print()


# ============================================================================
# STEP 6: Save regression-ready panel
# ============================================================================
print("[6/6] Saving regression-ready dataset...")

output_path = '03_Data_Clean/regression_panel_final.csv'
df.to_csv(output_path, index=False)

# Column count assertion: 11 input + 2 logs + 2 changes + 8 lags = 23
assert len(df.columns) == 23, f"Expected 23 columns, got {len(df.columns)}"

print("=" * 70)
print("VARIABLE ENGINEERING COMPLETE")
print("=" * 70)
print(f"Output:        {output_path}")
print(f"Total rows:    {len(df):,}")
print(f"Total columns: {len(df.columns)}")
print()
print("Variables created:")
print("  Logs:    log_deposits (offset +1), log_lights_qt (offset +0.001)")
print("  Changes: deposit_change_qt, lights_change_qt (log first differences)")
print("  Lags:    flood_ruleA_L1-L4, flood_ruleB_L1-L4")
print()
print("Missing values (structural -- from time-series operations):")
print(f"  Changes (L1): {df['deposit_change_qt'].isna().sum():,}  (expected 631 -- 1 per district)")
print(f"  Lag L1:       {df['flood_ruleA_L1'].isna().sum():,}  (expected 631)")
print(f"  Lag L2:       {df['flood_ruleA_L2'].isna().sum():,}  (expected 1,262)")
print(f"  Lag L3:       {df['flood_ruleA_L3'].isna().sum():,}  (expected 1,893)")
print(f"  Lag L4:       {df['flood_ruleA_L4'].isna().sum():,}  (expected 2,524)")
print()
print("=" * 70)
print("NEXT STEP: Run Script 25 (descriptive statistics)")
print("=" * 70)