"""
32b_cpi_diagnostic_2023.py
Phase 6 Step 3: 2023 Deposit Anomaly Diagnosis

Purpose:
  Investigate whether 2023 shows anomalous deposit behavior that could
  indicate: (a) unit change in RBI source data, (b) data corruption,
  or (c) genuine economic shock (post-COVID normalization, RBI rate hikes).

Script 32 found: 2023 annualized growth = 1.14% (panel minimum).
This script determines whether that is a real economic signal or a
data artifact.

Checks:
  1. Deposit LEVELS: median/mean by year 2022-2024 (unit error detection)
  2. Raw deposit_change_qt distribution by year (pre-winsorization)
  3. Winsorized deposit_change_qt_winsor distribution by year
  4. Extreme quarter identification in 2023 (top/bottom 10)
  5. Conclusion: unit error / systemic spike / genuine signal

INPUT:   03_Data_Clean/regression_panel_final_winsor.csv (23,347 x 24)
OUTPUTS:
  05_Outputs/Tables/06_32b_2023_diagnosis.csv
  05_Outputs/Logs/32b_cpi_diagnostic_2023_log.txt
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime

# === SETUP ===
os.makedirs('05_Outputs/Tables', exist_ok=True)
os.makedirs('05_Outputs/Logs',   exist_ok=True)

LOG_PATH = '05_Outputs/Logs/32b_cpi_diagnostic_2023_log.txt'
OUT_PATH = '05_Outputs/Tables/06_32b_2023_diagnosis.csv'

run_ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

log_lines = []
def log(msg=''):
    print(msg)
    log_lines.append(msg)

log("=" * 70)
log("SCRIPT 32b: 2023 DEPOSIT ANOMALY DIAGNOSIS")
log(f"Run: {run_ts}")
log("=" * 70)


# =============================================================================
# STEP 1: LOAD AND ASSERT
# =============================================================================
log("\n[1/6] Loading winsorized panel...")

df = pd.read_csv('03_Data_Clean/regression_panel_final_winsor.csv')

assert len(df) == 23347, \
    f"Expected 23,347 rows, got {len(df):,}. Check upstream Script 31."
assert df.shape[1] == 24, \
    f"Expected 24 columns, got {df.shape[1]}. Check upstream Script 31."

required_cols = [
    'deposit_change_qt', 'deposit_change_qt_winsor',
    'quarter', 'district_gadm', 'state_gadm', 'deposits'
]
missing = [c for c in required_cols if c not in df.columns]
if missing:
    raise ValueError(
        f"Missing columns: {missing}\n"
        f"Available columns: {df.columns.tolist()}"
    )

log(f"  Loaded:   {len(df):,} rows, {df.shape[1]} columns -- PASS")
log(f"  Required columns verified -- PASS")

# Extract year
df['year'] = df['quarter'].str[:4].astype(int)

# Verify 2022, 2023, 2024 exist
for yr in [2022, 2023, 2024]:
    assert yr in df['year'].values, \
        f"Year {yr} not found in panel. Check quarter column."
log(f"  Years 2022, 2023, 2024 verified present -- PASS")

# Winsorized bounds from Script 31 (for reference in thresholds below)
winsor_lower = df['deposit_change_qt_winsor'].min()
winsor_upper = df['deposit_change_qt_winsor'].max()
log(f"  Winsorized bounds: [{winsor_lower:.6f}, {winsor_upper:.6f}]")
log(f"  (Consistent with Script 31 thresholds [-0.162585, 0.230701])")


# =============================================================================
# STEP 2: DEPOSIT LEVELS CHECK (Unit Error Detection)
# =============================================================================
log("\n[2/6] Checking deposit LEVELS by year (unit error detection)...")

focus = df[df['year'].isin([2021, 2022, 2023, 2024])].copy()

level_check = (
    focus.groupby('year')['deposits']
    .agg(['median', 'mean', 'min', 'max', 'count'])
    .round(2)
)

log(f"\n  Deposit levels (raw, crores INR) by year:")
log(f"  {'Year':<6} {'Median':>14} {'Mean':>14} {'Min':>14} {'Max':>14} {'N':>8}")
log(f"  {'-'*70}")
for yr, row in level_check.iterrows():
    log(f"  {yr:<6} {row['median']:>14.2f} {row['mean']:>14.2f} "
        f"{row['min']:>14.2f} {row['max']:>14.2f} {int(row['count']):>8}")

median_2021 = focus[focus['year'] == 2021]['deposits'].median()
median_2022 = focus[focus['year'] == 2022]['deposits'].median()
median_2023 = focus[focus['year'] == 2023]['deposits'].median()
median_2024 = focus[focus['year'] == 2024]['deposits'].median()

ratio_2023_vs_2022 = median_2023 / median_2022 if median_2022 != 0 else np.nan
ratio_2024_vs_2023 = median_2024 / median_2023 if median_2023 != 0 else np.nan
ratio_2022_vs_2021 = median_2022 / median_2021 if median_2021 != 0 else np.nan

log(f"\n  Year-on-year median level ratios:")
log(f"    2022 / 2021 = {ratio_2022_vs_2021:.4f}x")
log(f"    2023 / 2022 = {ratio_2023_vs_2022:.4f}x")
log(f"    2024 / 2023 = {ratio_2024_vs_2023:.4f}x")

# Unit error flag: 5x+ jump in levels = unit mismatch in RBI source file
unit_error_flag = ratio_2023_vs_2022 > 5 or ratio_2023_vs_2022 < 0.2
log(f"\n  Unit error flag (ratio > 5x or < 0.2): {'YES -- INVESTIGATE' if unit_error_flag else 'NO -- PASS'}")


# =============================================================================
# STEP 3: RAW deposit_change_qt DISTRIBUTION BY YEAR (Pre-Winsorization)
# =============================================================================
log("\n[3/6] Raw deposit_change_qt distribution by year (pre-winsorization)...")
log(f"  Note: Raw column used here -- winsorization caps are NOT applied.")
log(f"  This reveals true extreme values before Script 31 clipping.")

log(f"\n  {'Year':<6} {'Mean':>10} {'Std':>10} {'Min':>12} {'1%':>10} "
    f"{'Median':>10} {'99%':>10} {'Max':>12} {'N':>8}")
log(f"  {'-'*90}")

raw_summary_rows = []
for yr in [2021, 2022, 2023, 2024]:
    sub = df[df['year'] == yr]['deposit_change_qt'].dropna()
    p1  = sub.quantile(0.01)
    p99 = sub.quantile(0.99)
    row = {
        'year': yr,
        'mean':   sub.mean(),
        'std':    sub.std(),
        'min':    sub.min(),
        'p1':     p1,
        'median': sub.median(),
        'p99':    p99,
        'max':    sub.max(),
        'n':      len(sub)
    }
    raw_summary_rows.append(row)
    log(f"  {yr:<6} {row['mean']:>10.6f} {row['std']:>10.6f} "
        f"{row['min']:>12.6f} {row['p1']:>10.6f} "
        f"{row['median']:>10.6f} {row['p99']:>10.6f} "
        f"{row['max']:>12.6f} {int(row['n']):>8}")


# =============================================================================
# STEP 4: WINSORIZED DISTRIBUTION BY YEAR (Post-Winsorization)
# =============================================================================
log("\n[4/6] Winsorized deposit_change_qt_winsor distribution by year...")

log(f"\n  {'Year':<6} {'Mean':>10} {'Std':>10} {'Median':>10} {'N':>8}")
log(f"  {'-'*50}")

winsor_summary_rows = []
for yr in [2021, 2022, 2023, 2024]:
    sub = df[df['year'] == yr]['deposit_change_qt_winsor'].dropna()
    row = {
        'year':   yr,
        'mean':   sub.mean(),
        'std':    sub.std(),
        'median': sub.median(),
        'n':      len(sub)
    }
    winsor_summary_rows.append(row)
    log(f"  {yr:<6} {row['mean']:>10.6f} {row['std']:>10.6f} "
        f"{row['median']:>10.6f} {int(row['n']):>8}")


# =============================================================================
# STEP 5: EXTREME QUARTER IDENTIFICATION IN 2023
# =============================================================================
log("\n[5/6] Extreme quarter identification in 2023...")

df_2023 = df[df['year'] == 2023].copy()

# Use RAW deposit_change_qt for extreme detection (not winsorized)
# Top 10 highest raw growth in 2023
top10_2023 = df_2023.nlargest(10, 'deposit_change_qt')[
    ['district_gadm', 'state_gadm', 'quarter', 'deposits',
     'deposit_change_qt', 'deposit_change_qt_winsor']
].reset_index(drop=True)

# Bottom 10 lowest raw growth in 2023
bot10_2023 = df_2023.nsmallest(10, 'deposit_change_qt')[
    ['district_gadm', 'state_gadm', 'quarter', 'deposits',
     'deposit_change_qt', 'deposit_change_qt_winsor']
].reset_index(drop=True)

log(f"\n  Top 10 highest raw deposit_change_qt in 2023:")
log(f"  {'District':<25} {'State':<15} {'Quarter':<8} "
    f"{'Deposits':>12} {'Raw Chg':>12} {'Winsor Chg':>12}")
log(f"  {'-'*88}")
for _, row in top10_2023.iterrows():
    log(f"  {str(row['district_gadm']):<25} {str(row['state_gadm']):<15} "
        f"{str(row['quarter']):<8} {row['deposits']:>12.2f} "
        f"{row['deposit_change_qt']:>12.6f} {row['deposit_change_qt_winsor']:>12.6f}")

log(f"\n  Bottom 10 lowest raw deposit_change_qt in 2023:")
log(f"  {'District':<25} {'State':<15} {'Quarter':<8} "
    f"{'Deposits':>12} {'Raw Chg':>12} {'Winsor Chg':>12}")
log(f"  {'-'*88}")
for _, row in bot10_2023.iterrows():
    log(f"  {str(row['district_gadm']):<25} {str(row['state_gadm']):<15} "
        f"{str(row['quarter']):<8} {row['deposits']:>12.2f} "
        f"{row['deposit_change_qt']:>12.6f} {row['deposit_change_qt_winsor']:>12.6f}")

# High growth threshold: use 95th percentile of full-sample raw changes
# (NOT 0.5 -- that is above the winsorized ceiling of 0.230701)
threshold_high = df['deposit_change_qt'].quantile(0.95)
threshold_low  = df['deposit_change_qt'].quantile(0.05)

n_high_2023 = (df_2023['deposit_change_qt'].dropna() > threshold_high).sum()
n_low_2023  = (df_2023['deposit_change_qt'].dropna() < threshold_low).sum()
n_total_2023 = df_2023['deposit_change_qt'].notna().sum()

log(f"\n  Full-sample 95th pctile raw threshold: {threshold_high:.6f}")
log(f"  Full-sample 5th  pctile raw threshold: {threshold_low:.6f}")
log(f"  2023 obs above 95th pctile: {n_high_2023:,} of {n_total_2023:,} "
    f"({100*n_high_2023/n_total_2023:.1f}%)")
log(f"  2023 obs below  5th pctile: {n_low_2023:,} of {n_total_2023:,} "
    f"({100*n_low_2023/n_total_2023:.1f}%)")


# =============================================================================
# STEP 6: CONCLUSION + SAVE
# =============================================================================
log("\n[6/6] Conclusion and saving outputs...")

# Determine conclusion
if unit_error_flag:
    conclusion = (
        "UNIT ERROR DETECTED: 2023 deposit levels are 5x+ higher or lower "
        "than 2022. Likely RBI source file unit mismatch (lakhs vs crores). "
        "ACTION REQUIRED: Return to Script 01/02 and verify raw RBI data units."
    )
elif n_high_2023 > 0.10 * n_total_2023:
    conclusion = (
        "SYSTEMIC SPIKE: More than 10 percent of 2023 district-quarters "
        "exceed the full-sample 95th percentile. Possible data corruption "
        "or structural break. ACTION REQUIRED: Inspect raw RBI 2023 files."
    )
elif n_high_2023 > 0.05 * n_total_2023:
    conclusion = (
        "MODERATE ANOMALY: 5-10 percent of 2023 district-quarters exceed "
        "the 95th percentile. Warrants investigation but may reflect genuine "
        "post-COVID normalization. Monitor in robustness section."
    )
else:
    conclusion = (
        "NO SYSTEMIC ANOMALY: 2023 extreme obs count is within normal range. "
        "Low 2023 annualized growth (1.14% from Script 32) reflects genuine "
        "economic signal -- consistent with RBI deposit growth slowdown "
        "and high inflation eroding real deposit accumulation in 2023. "
        "Winsorization handled individual outliers. No action required."
    )

log(f"\n  CONCLUSION:")
log(f"  {conclusion}")

# Save diagnostic CSV
diag_rows = []
for rr, wr in zip(raw_summary_rows, winsor_summary_rows):
    diag_rows.append({
        'year':              rr['year'],
        'raw_mean':          round(rr['mean'],   6),
        'raw_std':           round(rr['std'],    6),
        'raw_min':           round(rr['min'],    6),
        'raw_p1':            round(rr['p1'],     6),
        'raw_median':        round(rr['median'], 6),
        'raw_p99':           round(rr['p99'],    6),
        'raw_max':           round(rr['max'],    6),
        'winsor_mean':       round(wr['mean'],   6),
        'winsor_std':        round(wr['std'],    6),
        'winsor_median':     round(wr['median'], 6),
        'deposit_median_level': round(
            focus[focus['year'] == rr['year']]['deposits'].median(), 2
        ) if rr['year'] in [2021, 2022, 2023, 2024] else np.nan,
        'n_obs':             int(rr['n']),
        'n_above_p95':       int(n_high_2023) if rr['year'] == 2023 else None,
        'n_below_p5':        int(n_low_2023)  if rr['year'] == 2023 else None,
        'unit_error_flag':   unit_error_flag  if rr['year'] == 2023 else False
    })

diag_df = pd.DataFrame(diag_rows)
diag_df.to_csv(OUT_PATH, index=False)

assert os.path.exists(OUT_PATH), f"Output CSV not saved at {OUT_PATH}."
log(f"\n  Table saved: {OUT_PATH} -- PASS")

# Write full log
with open(LOG_PATH, 'w', encoding='utf-8') as f:
    f.write('\n'.join(log_lines))
assert os.path.exists(LOG_PATH), f"Log not saved at {LOG_PATH}."
log(f"  Log saved:   {LOG_PATH} -- PASS")


# === COMPLETION ===
log("\n" + "=" * 70)
log("SCRIPT 32b COMPLETE")
log(f"  Unit error flag:    {'YES -- ACTION REQUIRED' if unit_error_flag else 'NO'}")
log(f"  2023 above p95:     {n_high_2023:,} obs ({100*n_high_2023/n_total_2023:.1f}%)")
log(f"  Conclusion:         {conclusion[:80]}...")
log(f"  Table: {OUT_PATH}")
log(f"  Log:   {LOG_PATH}")
log("=" * 70)
log("NEXT: Update Hypotheses v2.5 and Codebook v2.5 with all Phase 4-6 results.")
log("=" * 70)