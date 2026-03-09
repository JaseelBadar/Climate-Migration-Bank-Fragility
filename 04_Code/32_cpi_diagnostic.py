"""
32_cpi_diagnostic.py
Phase 6 Step 2: CPI / Nominal-vs-Real Diagnostic

Purpose:
  Assess whether deposit_change_qt_winsor exhibits systematic nominal
  inflation trends that would require CPI deflation before regression.

Decision logged here feeds directly into paper Section: Data & Methods.
Pre-committed decision (Hypotheses v2.4): Keep nominal INR. Disclose
inflation confound. Do NOT deflate (CPI data unavailable at district-
quarter granularity; deflation would introduce interpolation noise
that exceeds the bias it corrects).

INPUT:   03_Data_Clean/regression_panel_final_winsor.csv (23,347 x 24)
OUTPUTS:
  05_Outputs/Figures/32_nominal_growth_trend.png
  05_Outputs/Logs/32_cpi_diagnostic_log.txt
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from datetime import datetime

# === SETUP ===
os.makedirs('05_Outputs/Figures', exist_ok=True)
os.makedirs('05_Outputs/Logs',   exist_ok=True)

LOG_PATH = '05_Outputs/Logs/32_cpi_diagnostic_log.txt'
FIG_PATH = '05_Outputs/Figures/32_nominal_growth_trend.png'

run_ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

log_lines = []
def log(msg=''):
    print(msg)
    log_lines.append(msg)

log("=" * 70)
log("SCRIPT 32: CPI / NOMINAL-VS-REAL DIAGNOSTIC")
log(f"Run: {run_ts}")
log("=" * 70)


# =============================================================================
# STEP 1: LOAD AND ASSERT
# =============================================================================
log("\n[1/5] Loading winsorized panel...")

df = pd.read_csv('03_Data_Clean/regression_panel_final_winsor.csv')

assert len(df) == 23347, \
    f"Expected 23,347 rows, got {len(df):,}. Check upstream Script 31."
assert df.shape[1] == 24, \
    f"Expected 24 columns, got {df.shape[1]}. Check upstream Script 31."
assert 'deposit_change_qt_winsor' in df.columns, \
    "Column 'deposit_change_qt_winsor' not found. Run Script 31 first."
assert 'deposit_change_qt' in df.columns, \
    "Column 'deposit_change_qt' not found. Check regression_panel_final_winsor.csv."
assert 'quarter' in df.columns, \
    "Column 'quarter' not found. Check regression_panel_final_winsor.csv."
assert 'district_gadm' in df.columns, \
    "Column 'district_gadm' not found. Check regression_panel_final_winsor.csv."
assert 'state_gadm' in df.columns, \
    "Column 'state_gadm' not found. Check regression_panel_final_winsor.csv."

log(f"  Loaded:   {len(df):,} rows, {df.shape[1]} columns -- PASS")
log(f"  Required columns verified -- PASS")


# =============================================================================
# STEP 2: EXTRACT AND VERIFY YEAR
# =============================================================================
log("\n[2/5] Extracting year from quarter column...")

# Verify format: must be "YYYYQn" e.g. "2015Q1"
sample_quarters = df['quarter'].dropna().unique()[:5]
for q in sample_quarters:
    assert len(str(q)) == 6 and str(q)[4] == 'Q', \
        f"Unexpected quarter format: '{q}'. Expected 'YYYYQn'."

df['year'] = df['quarter'].str[:4].astype(int)

year_min = df['year'].min()
year_max = df['year'].max()

assert year_min == 2015, \
    f"Expected year_min=2015, got {year_min}. Check panel coverage."
assert year_max == 2024, \
    f"Expected year_max=2024, got {year_max}. Check panel coverage."

n_years    = df['year'].nunique()
n_quarters = df['quarter'].nunique()

log(f"  Year range: {year_min} - {year_max} -- PASS")
log(f"  Unique years:    {n_years}  (expected 10)")
log(f"  Unique quarters: {n_quarters}  (expected 36)")

assert n_years == 10, \
    f"Expected 10 years, got {n_years}."

# Full panel has 37 quarters (631 x 37 = 23,347).
# Regression-ready subset (after dropna on deposit_change_qt) has 36.
# One quarter exists in raw panel with all-NaN deposit_change_qt.
# Identify it here and document.

all_quarters_sorted = sorted(df['quarter'].unique().tolist())
log(f"\n  All {n_quarters} quarters in full panel:")
for i, q in enumerate(all_quarters_sorted):
    log(f"    {i+1:>3}. {q}")

# Identify which quarter(s) have zero valid deposit observations
qt_valid = (
    df.groupby('quarter')['deposit_change_qt']
    .apply(lambda x: x.notna().sum())
    .reset_index()
    .rename(columns={'deposit_change_qt': 'valid_deposit_obs'})
)
qt_zero = qt_valid[qt_valid['valid_deposit_obs'] == 0]
qt_low   = qt_valid[qt_valid['valid_deposit_obs'] < 50]

log(f"\n  Quarters with ZERO valid deposit_change_qt obs: {len(qt_zero)}")
for _, row in qt_zero.iterrows():
    log(f"    --> {row['quarter']}  (0 valid obs -- absent from regression)")

log(f"\n  Quarters with <50 valid deposit_change_qt obs:")
for _, row in qt_low.iterrows():
    log(f"    --> {row['quarter']}  ({int(row['valid_deposit_obs'])} valid obs)")

assert n_quarters in [36, 37], \
    f"Unexpected quarter count {n_quarters}. Expected 36 (regression) or 37 (full panel)."
log(f"\n  Quarter count {n_quarters} verified against full panel -- PASS")
log(f"  Note: regression subset has 36 quarters (1 quarter all-NaN, dropped by dropna)")


# =============================================================================
# STEP 3: COMPUTE NOMINAL GROWTH DIAGNOSTICS
# =============================================================================
log("\n[3/5] Computing nominal growth diagnostics...")

# Use winsorized variable throughout (this is the robustness dataset)
growth_by_year = (
    df.groupby('year')['deposit_change_qt_winsor']
    .agg(['mean', 'std', 'count'])
    .round(6)
)

# Annualize: compound quarterly rate to annual
# Formula: (1 + r_q)^4 - 1 where r_q is mean quarterly growth rate
# Labeled explicitly as simple-mean-based annualization (not geometric)
growth_by_year['annualized_pct'] = (
    ((1 + growth_by_year['mean']) ** 4 - 1) * 100
).round(4)

# Summary stats
mean_annualized    = growth_by_year['annualized_pct'].mean()
median_annualized  = growth_by_year['annualized_pct'].median()
min_annualized     = growth_by_year['annualized_pct'].min()
max_annualized     = growth_by_year['annualized_pct'].max()
min_year           = growth_by_year['annualized_pct'].idxmin()
max_year           = growth_by_year['annualized_pct'].idxmax()

log(f"\n  Annualized nominal deposit growth by year:")
log(f"  {'Year':<6} {'Mean Qtrly':>12} {'Std':>10} {'N':>8} {'Ann. %':>10}")
log(f"  {'-'*50}")
for yr, row in growth_by_year.iterrows():
    log(f"  {yr:<6} {row['mean']:>12.6f} {row['std']:>10.6f} "
        f"{int(row['count']):>8} {row['annualized_pct']:>10.4f}%")

log(f"\n  Summary (annualized %):")
log(f"    Simple mean:    {mean_annualized:.2f}%")
log(f"    Median:         {median_annualized:.2f}%")
log(f"    Min:            {min_annualized:.2f}% ({min_year})")
log(f"    Max:            {max_annualized:.2f}% ({max_year})")
log(f"\n  Note: 'Simple mean' = unweighted mean of annual rates across years.")
log(f"        Not a geometric mean. Used for diagnostic only, not regression.")


# =============================================================================
# STEP 4: PLOT
# =============================================================================
log("\n[4/5] Generating nominal growth trend figure...")

fig, ax = plt.subplots(figsize=(11, 6))

ax.plot(
    growth_by_year.index,
    growth_by_year['annualized_pct'],
    marker='o', linewidth=2.5, markersize=8,
    color='#1f77b4', label='Annualized nominal growth'
)
ax.axhline(
    mean_annualized,
    color='red', linestyle='--', linewidth=1.5, alpha=0.7,
    label=f'Simple mean: {mean_annualized:.1f}%'
)
ax.axhline(0, color='black', linewidth=0.8, alpha=0.4)

ax.set_title(
    'Annualized Nominal Deposit Growth Rate by Year\n'
    '(deposit_change_qt_winsor, 631 Districts, 2015-2024)',
    fontsize=13, fontweight='bold', pad=15
)
ax.set_xlabel('Year', fontsize=12)
ax.set_ylabel('Annualized Growth (%)', fontsize=12)
ax.set_xticks(growth_by_year.index)
ax.tick_params(axis='x', rotation=45)
ax.grid(True, alpha=0.3)
ax.legend(fontsize=11)

plt.tight_layout()
plt.savefig(FIG_PATH, dpi=300, bbox_inches='tight')
plt.close()

assert os.path.exists(FIG_PATH), \
    f"Figure not saved at {FIG_PATH}. Check matplotlib backend."
fig_size_kb = os.path.getsize(FIG_PATH) / 1024
assert fig_size_kb > 10, \
    f"Figure file suspiciously small ({fig_size_kb:.1f} KB). May be corrupted."

log(f"  Figure saved: {FIG_PATH} ({fig_size_kb:.1f} KB) -- PASS")


# =============================================================================
# STEP 5: DECISION LOG + SAVE
# =============================================================================
log("\n[5/5] Logging decision and saving outputs...")

DECISION = (
    "DECISION: Keep nominal INR. Do NOT deflate by CPI.\n"
    "Rationale: District-quarter CPI unavailable at required granularity.\n"
    "Interpolated CPI would introduce noise exceeding the bias it corrects.\n"
    "Paper disclosure: 'Deposits measured in nominal INR. India CPI inflation\n"
    "averaged ~6-7% annually 2015-2024. All regressions include quarter FE,\n"
    "which absorb national-level price trends. Remaining inflation confound\n"
    "is acknowledged as a limitation.'\n"
    "Pre-committed in Hypotheses v2.4."
)

log(f"\n  {DECISION}")

# Write full log to file
with open(LOG_PATH, 'w', encoding='utf-8') as f:
    f.write('\n'.join(log_lines))

assert os.path.exists(LOG_PATH), \
    f"Log not saved at {LOG_PATH}."
log(f"  Log saved: {LOG_PATH} -- PASS")


# === COMPLETION ===
log("\n" + "=" * 70)
log("SCRIPT 32 COMPLETE")
log(f"  Mean annualized nominal growth: {mean_annualized:.2f}%")
log(f"  Decision: Nominal INR retained. Quarter FE absorb price trends.")
log(f"  Figure: {FIG_PATH}")
log(f"  Log:    {LOG_PATH}")
log("=" * 70)
log("NEXT: Script 32b -- 2023 CPI spike diagnosis.")
log("=" * 70)