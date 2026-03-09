"""
31_winsorize.py
Robustness: Winsorize deposit_change_qt at 1st/99th percentile.
Produces regression_panel_final_winsor.csv for use in downstream
robustness re-runs of Scripts 27-30.

Winsorization is applied ONLY to deposit_change_qt (dependent variable).
flood_exposure_ruleA/B_qt are counts (bounded below at 0, no upper outlier risk).
log_lights_qt is log-transformed (outlier risk already mitigated).

OUTPUT:
  03_Data_Clean/regression_panel_final_winsor.csv  -- full panel + winsorized column
  05_Outputs/Logs/31_winsorize_log.txt             -- full execution log
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime

# === SETUP ===
os.makedirs('03_Data_Clean',    exist_ok=True)
os.makedirs('05_Outputs/Logs',  exist_ok=True)

LOG_PATH = '05_Outputs/Logs/31_winsorize_log.txt'
OUT_PATH = '03_Data_Clean/regression_panel_final_winsor.csv'

run_ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

log_lines = []
def log(msg=''):
    print(msg)
    log_lines.append(msg)

log("=" * 70)
log("SCRIPT 31: WINSORIZE deposit_change_qt (1%/99%) -- Robustness Prep")
log(f"Run: {run_ts}")
log("=" * 70)


# =============================================================================
# STEP 1: LOAD AND ASSERT
# =============================================================================
log("\n[1/5] Loading regression-ready panel...")

df = pd.read_csv('03_Data_Clean/regression_panel_final.csv')

assert len(df) == 23347, \
    f"Expected 23,347 rows, got {len(df):,}. Check upstream pipeline."
assert df.shape[1] == 23, \
    f"Expected 23 columns, got {df.shape[1]}. Check upstream pipeline."
assert 'deposit_change_qt' in df.columns, \
    "Column 'deposit_change_qt' not found. Check regression_panel_final.csv."
assert 'flood_exposure_ruleA_qt' in df.columns, \
    "Column 'flood_exposure_ruleA_qt' not found."
assert 'flood_exposure_ruleB_qt' in df.columns, \
    "Column 'flood_exposure_ruleB_qt' not found."

log(f"  Loaded:   {len(df):,} rows, {df.shape[1]} columns -- PASS")
log(f"  Required columns verified -- PASS")

nan_count = df['deposit_change_qt'].isna().sum()
valid_n   = df['deposit_change_qt'].notna().sum()
log(f"  deposit_change_qt: {valid_n:,} valid | {nan_count:,} NaN")


# =============================================================================
# STEP 2: PRE-WINSORIZE DESCRIPTIVES
# =============================================================================
log("\n[2/5] Pre-winsorize descriptives (deposit_change_qt)...")

pre = df['deposit_change_qt'].describe(percentiles=[0.01, 0.05, 0.25, 0.50, 0.75, 0.95, 0.99])

log(f"  count   = {pre['count']:>12,.0f}")
log(f"  mean    = {pre['mean']:>12.6f}")
log(f"  std     = {pre['std']:>12.6f}")
log(f"  min     = {pre['min']:>12.6f}")
log(f"  1%      = {pre['1%']:>12.6f}")
log(f"  5%      = {pre['5%']:>12.6f}")
log(f"  25%     = {pre['25%']:>12.6f}")
log(f"  median  = {pre['50%']:>12.6f}")
log(f"  75%     = {pre['75%']:>12.6f}")
log(f"  95%     = {pre['95%']:>12.6f}")
log(f"  99%     = {pre['99%']:>12.6f}")
log(f"  max     = {pre['max']:>12.6f}")


# =============================================================================
# STEP 3: WINSORIZE
# =============================================================================
log("\n[3/5] Winsorizing at 1st / 99th percentile...")

# Compute thresholds on NON-NaN values only
lower = df['deposit_change_qt'].quantile(0.01)
upper = df['deposit_change_qt'].quantile(0.99)

log(f"  Lower threshold (1%):  {lower:.6f}")
log(f"  Upper threshold (99%): {upper:.6f}")

# Apply winsorization -- NaN values remain NaN (not clipped to bounds)
df['deposit_change_qt_winsor'] = np.where(
    df['deposit_change_qt'].isna(),
    np.nan,
    np.clip(df['deposit_change_qt'], lower, upper)
)

# Count clipped obs (from non-NaN pool only)
n_clipped_low  = (df['deposit_change_qt'].notna() & (df['deposit_change_qt'] < lower)).sum()
n_clipped_high = (df['deposit_change_qt'].notna() & (df['deposit_change_qt'] > upper)).sum()
n_clipped_total = n_clipped_low + n_clipped_high
pct_clipped = (n_clipped_total / valid_n) * 100

log(f"  Clipped below lower:  {n_clipped_low:,} obs")
log(f"  Clipped above upper:  {n_clipped_high:,} obs")
log(f"  Total clipped:        {n_clipped_total:,} obs ({pct_clipped:.2f}% of valid N)")


# =============================================================================
# STEP 4: POST-WINSORIZE DESCRIPTIVES
# =============================================================================
log("\n[4/5] Post-winsorize descriptives (deposit_change_qt_winsor)...")

post = df['deposit_change_qt_winsor'].describe(percentiles=[0.01, 0.05, 0.25, 0.50, 0.75, 0.95, 0.99])

log(f"  count   = {post['count']:>12,.0f}")
log(f"  mean    = {post['mean']:>12.6f}")
log(f"  std     = {post['std']:>12.6f}")
log(f"  min     = {post['min']:>12.6f}")
log(f"  1%      = {post['1%']:>12.6f}")
log(f"  5%      = {post['5%']:>12.6f}")
log(f"  25%     = {post['25%']:>12.6f}")
log(f"  median  = {post['50%']:>12.6f}")
log(f"  75%     = {post['75%']:>12.6f}")
log(f"  95%     = {post['95%']:>12.6f}")
log(f"  99%     = {post['99%']:>12.6f}")
log(f"  max     = {post['max']:>12.6f}")

# Verify winsorization bounds are exactly at thresholds
assert df['deposit_change_qt_winsor'].min() >= lower - 1e-10, \
    "Winsorization failed: min below lower threshold."
assert df['deposit_change_qt_winsor'].max() <= upper + 1e-10, \
    "Winsorization failed: max above upper threshold."
log(f"\n  Bounds verified (min >= lower, max <= upper) -- PASS")

# Verify NaN count unchanged
nan_winsor = df['deposit_change_qt_winsor'].isna().sum()
assert nan_winsor == nan_count, \
    f"NaN count changed after winsorization: {nan_count} -> {nan_winsor}. Check np.where logic."
log(f"  NaN count unchanged ({nan_count:,}) -- PASS")


# =============================================================================
# STEP 5: SAVE OUTPUTS
# =============================================================================
log("\n[5/5] Saving outputs...")

# Verify column count: original 23 + 1 winsorized = 24
assert df.shape[1] == 24, \
    f"Expected 24 columns in output, got {df.shape[1]}."

df.to_csv(OUT_PATH, index=False)

# Verify saved CSV row count
df_check = pd.read_csv(OUT_PATH)
assert len(df_check) == 23347, \
    f"Output CSV has {len(df_check):,} rows, expected 23,347. Save failed."
assert df_check.shape[1] == 24, \
    f"Output CSV has {df_check.shape[1]} columns, expected 24. Save failed."
del df_check

log(f"  Output CSV verified: 23,347 rows, 24 columns -- PASS")
log(f"  Saved: {OUT_PATH}")

# Write log
with open(LOG_PATH, 'w', encoding='utf-8') as f:
    f.write('\n'.join(log_lines))
log(f"  Log:   {LOG_PATH}")


# === COMPLETION ===
log("\n" + "=" * 70)
log("SCRIPT 31 COMPLETE")
log(f"  deposit_change_qt_winsor: thresholds [{lower:.6f}, {upper:.6f}]")
log(f"  Clipped: {n_clipped_total:,} obs ({pct_clipped:.2f}%)")
log(f"  Output: {OUT_PATH}")
log("=" * 70)
log("NEXT: Script 32 CPI diagnosis on regression_panel_final_winsor.csv")
log("=" * 70)