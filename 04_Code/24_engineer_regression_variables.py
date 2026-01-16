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
print(f"  ✓ Loaded: {len(df):,} rows")
print(f"  ✓ Columns: {df.columns.tolist()}")
print()

# ============================================================================
# STEP 2: Sort by district-quarter (critical for time-series operations)
# ============================================================================
print("[2/6] Sorting by district-quarter...")
df = df.sort_values(['district_gadm', 'state_gadm', 'year', 'q'])
print("  ✓ Sorted")
print()

# ============================================================================
# STEP 3: Create log variables (for elasticities)
# ============================================================================
print("[3/6] Creating log variables...")

# Log of deposits (₹ Crores)
df['log_deposits'] = np.log(df['deposits'] + 1)  # log(x+1) to handle zeros

# Log of nighttime lights (nW/cm²/sr)
df['log_lights_qt'] = np.log(df['mean_radiance'] + 1)  # log(x+1) to handle zeros

print("  ✓ log_deposits created")
print("  ✓ log_lights_qt created")
print()

# ============================================================================
# STEP 4: Create quarter-over-quarter changes (growth rates)
# ============================================================================
print("[4/6] Computing quarter-over-quarter changes...")

# First differences (within district)
df['deposit_change_qt'] = df.groupby(['district_gadm', 'state_gadm'])['log_deposits'].diff()
df['lights_change_qt'] = df.groupby(['district_gadm', 'state_gadm'])['log_lights_qt'].diff()

print("  ✓ deposit_change_qt created")
print("  ✓ lights_change_qt created")
print()

# ============================================================================
# STEP 5: Create lagged flood variables (for distributed lag models)
# ============================================================================
print("[5/6] Creating lagged flood exposure variables...")

# Lag 1 quarter (t-1)
df['flood_ruleA_L1'] = df.groupby(['district_gadm', 'state_gadm'])['flood_exposure_ruleA_qt'].shift(1)
df['flood_ruleB_L1'] = df.groupby(['district_gadm', 'state_gadm'])['flood_exposure_ruleB_qt'].shift(1)

# Lag 2 quarters (t-2)
df['flood_ruleA_L2'] = df.groupby(['district_gadm', 'state_gadm'])['flood_exposure_ruleA_qt'].shift(2)
df['flood_ruleB_L2'] = df.groupby(['district_gadm', 'state_gadm'])['flood_exposure_ruleB_qt'].shift(2)

# Lag 3 quarters (t-3)
df['flood_ruleA_L3'] = df.groupby(['district_gadm', 'state_gadm'])['flood_exposure_ruleA_qt'].shift(3)
df['flood_ruleB_L3'] = df.groupby(['district_gadm', 'state_gadm'])['flood_exposure_ruleB_qt'].shift(3)

# Lag 4 quarters (t-4, one year)
df['flood_ruleA_L4'] = df.groupby(['district_gadm', 'state_gadm'])['flood_exposure_ruleA_qt'].shift(4)
df['flood_ruleB_L4'] = df.groupby(['district_gadm', 'state_gadm'])['flood_exposure_ruleB_qt'].shift(4)

print("  ✓ Lags L1-L4 created for Rule A and Rule B")
print()

# ============================================================================
# STEP 6: Save regression-ready panel
# ============================================================================
print("[6/6] Saving regression-ready dataset...")

output_path = '03_Data_Clean/regression_panel_final.csv'
df.to_csv(output_path, index=False)

print("=" * 70)
print("VARIABLE ENGINEERING COMPLETE")
print("=" * 70)
print(f"Output: {output_path}")
print(f"Total rows: {len(df):,}")
print(f"Total columns: {len(df.columns)}")
print()
print("Variables created:")
print("  Logs: log_deposits, log_lights_qt")
print("  Changes: deposit_change_qt, lights_change_qt")
print("  Lags: flood_ruleA_L1 to L4, flood_ruleB_L1 to L4")
print()
print("Missing values (expected for lags):")
print(f"  - L1 lags: {df['flood_ruleA_L1'].isna().sum():,} obs")
print(f"  - L2 lags: {df['flood_ruleA_L2'].isna().sum():,} obs")
print(f"  - L3 lags: {df['flood_ruleA_L3'].isna().sum():,} obs")
print(f"  - L4 lags: {df['flood_ruleA_L4'].isna().sum():,} obs")
print()
print("=" * 70)
print()
print("NEXT STEP: Run Script 25 (descriptive statistics)")
print("=" * 70)