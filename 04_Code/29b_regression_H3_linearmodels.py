"""
29b_regression_H3_linearmodels.py
H3: Distributed Lag -- Flood Timing -> Deposit Withdrawals
Tests whether flood-induced deposit stress is contemporaneous, 1Q lagged, or 2Q lagged.

PRE-COMMITTED SPECIFICATION: Time (quarter) FE only. NO entity (district) FE.
Rationale: deposit_change_qt is log-differenced -- district-level trends absorbed
by differencing. District FE in a differenced spec is not part of the pre-committed
H3 design (Hypotheses v2.4, Section H3a). H3 was validated as clean -- unaffected
by any pipeline contamination event (no VIIRS, no district FE, no homonymous
FE collapse).

Replaces Script 29 (statsmodels OLS). Key differences:
  1. linearmodels PanelOLS with time_effects=True, entity_effects=False.
     Equivalent to statsmodels OLS + C(quarter) dummies but without the
     ValueWarning from rank deficiency in clustered VCV at 666 exog columns.
  2. Panel index uses quarter_int (sequential integer). Identical fix to Scripts 27b/28b.
  3. SE: cluster_entity=True (clustered by district_state_id, 631 clusters).

Anchors (Script 29, statsmodels -- Pre-Writing Master Plan, Section 1):
  Rule A t0:  beta =  0.000609, SE = 0.001463, p = 0.677  -- NULL
  Rule A t-1: beta =  0.001505, SE = 0.001114, p = 0.177  -- NULL
  Rule A t-2: beta = -0.007005, SE = 0.001645, p < 0.001  -- CONFIRMED
  Rule B: all lags null (0.90% treatment rate, insufficient power)
  N = 21,837 | Quarter FE = 35 | NO district FE

Output: 05_Outputs/Tables/04b_H3_linearmodels.csv
        05_Outputs/Logs/29b_H3_linearmodels.txt
        05_Outputs/Logs/29b_H3_linearmodels_full_ruleA.txt
        05_Outputs/Logs/29b_H3_linearmodels_full_ruleB.txt
"""

import os
import numpy as np
import pandas as pd
import logging
from linearmodels import PanelOLS

# =============================================================================
# [1/7] SETUP
# =============================================================================

os.makedirs('05_Outputs/Logs',   exist_ok=True)
os.makedirs('05_Outputs/Tables', exist_ok=True)

logging.basicConfig(
    filename='05_Outputs/Logs/29b_H3_linearmodels.txt',
    level=logging.INFO,
    format='%(message)s',
    filemode='w'
)
log = logging.getLogger(__name__)

# Stability threshold: flag if linearmodels beta differs from Script 29 anchor.
# H3 t-2 Rule A is the primary confirmed result. Applied to all 3 Rule A lags.
# Rule B anchors are all null; threshold applied for completeness.
STABILITY_THRESHOLD = 0.001

# Confirmed anchors from Script 29 (Pre-Writing Master Plan, Section 1, locked).
ANCHOR_A_T0_BETA  =  0.000609
ANCHOR_A_T0_SE    =  0.001463
ANCHOR_A_T1_BETA  =  0.001505
ANCHOR_A_T1_SE    =  0.001114
ANCHOR_A_T2_BETA  = -0.007005   # PRIMARY RESULT -- confirmed Mar 8
ANCHOR_A_T2_SE    =  0.001645
# Rule B: all null. Coefficients not pre-specified beyond null expectation.
ANCHOR_B_T0_BETA  = np.nan
ANCHOR_B_T1_BETA  = np.nan
ANCHOR_B_T2_BETA  = np.nan

ANCHOR_N          = 21837
ANCHOR_QFE        = 35

def _stars(p):
    if p < 0.001: return "***"
    if p < 0.01:  return "**"
    if p < 0.05:  return "*"
    if p < 0.10:  return "+"
    return ""

print("=" * 70)
print("SCRIPT 29b: H3 DISTRIBUTED LAG -- linearmodels PanelOLS")
print("Flood Timing -> Deposit Withdrawals")
print("=" * 70)
log.info("=" * 70)
log.info("29b: H3 DISTRIBUTED LAG -- linearmodels PanelOLS")
log.info("Flood Timing -> Deposit Withdrawals")
log.info("SPECIFICATION: time_effects=True, entity_effects=False (pre-committed)")
log.info("Anchors (Script 29, statsmodels):")
log.info(f"  Rule A t0:  beta={ANCHOR_A_T0_BETA}, SE={ANCHOR_A_T0_SE}, p=0.677 -- NULL")
log.info(f"  Rule A t-1: beta={ANCHOR_A_T1_BETA}, SE={ANCHOR_A_T1_SE}, p=0.177 -- NULL")
log.info(f"  Rule A t-2: beta={ANCHOR_A_T2_BETA}, SE={ANCHOR_A_T2_SE}, p<0.001 -- CONFIRMED")
log.info(f"  Rule B: all lags null (0.90% treatment rate)")
log.info(f"  N={ANCHOR_N}, Quarter FE={ANCHOR_QFE}, NO district FE")
log.info("=" * 70)

# =============================================================================
# [2/7] LOAD AND VALIDATE DATA
# =============================================================================

print("\n[2/7] Loading regression-ready panel...")
log.info("\n[2/7] Loading data")

df = pd.read_csv('03_Data_Clean/regression_panel_final.csv')
assert len(df) == 23347, f"Expected 23,347 rows, got {len(df):,}"
assert df.shape[1] == 23,  f"Expected 23 columns, got {df.shape[1]}"
print(f"  Loaded: {len(df):,} rows, {df.shape[1]} columns -- PASS")
log.info(f"  Loaded: {len(df):,} rows, {df.shape[1]} columns -- PASS")

required_cols = [
    'deposit_change_qt',
    'flood_exposure_ruleA_qt', 'flood_ruleA_L1', 'flood_ruleA_L2',
    'flood_exposure_ruleB_qt', 'flood_ruleB_L1', 'flood_ruleB_L2',
    'district_gadm', 'state_gadm', 'quarter'
]
missing_cols = [c for c in required_cols if c not in df.columns]
assert len(missing_cols) == 0, f"Missing required columns: {missing_cols}"
print(f"  Required columns verified -- PASS")
log.info(f"  Required columns verified -- PASS")

# =============================================================================
# [3/7] COMPOSITE KEY, LAG VERIFICATION, COMPLETE CASES
# =============================================================================

print("\n[3/7] Composite key, lag arithmetic, complete cases...")
log.info("\n[3/7] Composite key, lag arithmetic, complete cases")

# Composite key: prevents 7 homonymous district pairs from collapsing in clustering.
# district_gadm alone -> 624 FE (WRONG). Composite -> 631 (CORRECT).
# Note: composite key is used for entity index (panel clustering) only.
# NO district FE in H3 -- pre-committed specification.
df['district_state_id'] = df['district_gadm'] + '_' + df['state_gadm']
n_districts_full = df['district_state_id'].nunique()
assert n_districts_full == 631, (
    f"Expected 631 district_state_id. Got {n_districts_full}. Check composite key."
)
print(f"  district_state_id: {n_districts_full} unique pairs -- PASS")
log.info(f"  district_state_id: {n_districts_full} -- PASS")

# Verify pre-computed lag arithmetic from Script 24.
# L1: one quarter lag -- NaN for first quarter per district (631 NaN).
# L2: two quarter lag -- NaN for first two quarters per district (1,262 NaN).
nan_check = {
    'flood_exposure_ruleA_qt': (0,    "expected 0"),
    'flood_ruleA_L1':          (631,  "expected 631"),
    'flood_ruleA_L2':          (1262, "expected 1,262"),
    'flood_exposure_ruleB_qt': (0,    "expected 0"),
    'flood_ruleB_L1':          (631,  "expected 631"),
    'flood_ruleB_L2':          (1262, "expected 1,262"),
}
for col, (expected_nan, label) in nan_check.items():
    actual_nan = df[col].isna().sum()
    assert actual_nan == expected_nan, (
        f"Lag NaN mismatch for {col}: expected {expected_nan}, got {actual_nan}. "
        f"Check Script 24 lag construction."
    )
    print(f"  {col} NaN: {actual_nan:,}  ({label}) -- PASS")
    log.info(f"  {col} NaN: {actual_nan:,}  ({label}) -- PASS")

# Restrict to complete cases.
# H3 complete case: deposit_change_qt + all lag flood columns non-NaN.
# L2 is the binding constraint (2 quarters dropped per district = 1,262 NaN).
# Additional deposit NaN (~274 beyond first quarter) reduces further.
initial_n = len(df)

df_A = df[
    df['deposit_change_qt'].notna()       &
    df['flood_exposure_ruleA_qt'].notna() &
    df['flood_ruleA_L1'].notna()          &
    df['flood_ruleA_L2'].notna()
].copy().reset_index(drop=True)

df_B = df[
    df['deposit_change_qt'].notna()       &
    df['flood_exposure_ruleB_qt'].notna() &
    df['flood_ruleB_L1'].notna()          &
    df['flood_ruleB_L2'].notna()
].copy().reset_index(drop=True)

dropped_A = initial_n - len(df_A)
dropped_B = initial_n - len(df_B)

assert 21500 <= len(df_A) <= 22200, (
    f"Rule A sample {len(df_A):,} outside expected range [21,500, 22,200]. "
    f"Expected ~{ANCHOR_N:,}. Check lag and deposit NaN structure."
)
assert 21500 <= len(df_B) <= 22200, (
    f"Rule B sample {len(df_B):,} outside expected range [21,500, 22,200]. "
    f"Expected ~{ANCHOR_N:,}. Check lag and deposit NaN structure."
)

print(f"  Initial:               {initial_n:,} obs")
print(f"  After restriction (A): {len(df_A):,} obs  (anchor: {ANCHOR_N:,})")
print(f"  After restriction (B): {len(df_B):,} obs  (anchor: {ANCHOR_N:,})")
print(f"  Dropped (A):           {dropped_A:,} obs ({dropped_A / initial_n * 100:.1f}%)")
print(f"  Dropped (B):           {dropped_B:,} obs ({dropped_B / initial_n * 100:.1f}%)")
log.info(f"  Initial: {initial_n:,}")
log.info(f"  After restriction (A): {len(df_A):,}  (anchor: {ANCHOR_N:,})")
log.info(f"  After restriction (B): {len(df_B):,}  (anchor: {ANCHOR_N:,})")
log.info(f"  Dropped (A): {dropped_A:,} ({dropped_A / initial_n * 100:.1f}%)")
log.info(f"  Dropped (B): {dropped_B:,} ({dropped_B / initial_n * 100:.1f}%)")

# =============================================================================
# [4/7] BUILD PANEL INDICES FOR linearmodels
# =============================================================================

print("\n[4/7] Building panel indices for linearmodels PanelOLS...")
log.info("\n[4/7] Building panel indices")

# linearmodels requires the time index to be numeric or date-like.
# 'quarter' stores strings e.g. '2015Q3' -- not accepted.
# Map to sequential integers (identical approach to Scripts 27b/28b).
# H3 sample starts at 2015Q3 (L2 drops 2015Q1 and 2015Q2 per district).
# Quarters sorted as strings are chronologically correct ('YYYYQN' format).

def build_panel_index(df_panel, label):
    """
    Add quarter_int column and set (district_state_id, quarter_int) MultiIndex.
    Returns indexed DataFrame and sorted quarter list.
    """
    quarters_sorted = sorted(df_panel['quarter'].unique())
    assert 33 <= len(quarters_sorted) <= 38, (
        f"Rule {label}: quarter count {len(quarters_sorted)} outside expected "
        f"range [33, 38]. Expected ~{ANCHOR_QFE}. "
        f"Range: {quarters_sorted[0]} to {quarters_sorted[-1]}."
    )
    quarter_to_int = {q: i for i, q in enumerate(quarters_sorted, start=1)}
    df_panel = df_panel.copy()
    df_panel['quarter_int'] = df_panel['quarter'].map(quarter_to_int)
    df_panel = df_panel.set_index(['district_state_id', 'quarter_int'])
    n_dup = df_panel.index.duplicated().sum()
    assert n_dup == 0, (
        f"Rule {label}: panel index has {n_dup} duplicate (entity, time) pairs."
    )
    print(f"  Rule {label}: {len(quarters_sorted)} quarters "
          f"({quarters_sorted[0]} to {quarters_sorted[-1]}, "
          f"mapped to integers 1-{len(quarters_sorted)}), "
          f"{df_panel.index.get_level_values(0).nunique()} entities, "
          f"{n_dup} duplicates -- PASS")
    log.info(f"  Rule {label}: {len(quarters_sorted)} quarters "
             f"({quarters_sorted[0]} to {quarters_sorted[-1]}), "
             f"{df_panel.index.get_level_values(0).nunique()} entities, "
             f"{n_dup} duplicates -- PASS")
    return df_panel, quarters_sorted

df_A, quarters_A = build_panel_index(df_A, 'A')
df_B, quarters_B = build_panel_index(df_B, 'B')

# =============================================================================
# [5/7] FIT MODELS: RULE A AND RULE B
# =============================================================================

print("\n[5/7] Fitting linearmodels PanelOLS models...")
log.info("\n[5/7] Model fitting")
log.info("  Specification: time_effects=True, entity_effects=False")
log.info("  Equivalent to: OLS + C(quarter) dummies (pre-committed H3 spec)")
log.info("  NO district (entity) FE -- deposit_change_qt is log-differenced;")
log.info("  district trends absorbed by differencing. Pre-committed H3 design.")
log.info("  SE: cluster_entity=True (clustered by district_state_id, 631 clusters)")

def fit_h3(df_panel, flood_col_t0, flood_col_t1, flood_col_t2,
           rule_label, quarters_sorted,
           anchor_t0, anchor_t1, anchor_t2):
    """
    Fit linearmodels PanelOLS for H3 distributed lag.
    time_effects=True, entity_effects=False (quarter FE only, no district FE).
    Returns result object and extracted scalars for all 3 lags.
    """
    log.info(f"\n  Rule {rule_label}:")
    log.info(f"    t0:  {flood_col_t0}")
    log.info(f"    t-1: {flood_col_t1}")
    log.info(f"    t-2: {flood_col_t2}")

    exog = df_panel[[flood_col_t0, flood_col_t1, flood_col_t2]]

    model = PanelOLS(
        dependent      = df_panel['deposit_change_qt'],
        exog           = exog,
        entity_effects = False,
        time_effects   = True
    )

    result = model.fit(
        cov_type       = 'clustered',
        cluster_entity = True
    )

    def _extract(varname):
        beta  = result.params[varname]
        se    = result.std_errors[varname]
        t     = result.tstats[varname]
        p     = result.pvalues[varname]
        ci    = result.conf_int()
        ci_lo = ci.loc[varname, 'lower']
        ci_hi = ci.loc[varname, 'upper']
        sig   = _stars(p)
        return beta, se, t, p, ci_lo, ci_hi, sig

    b_t0, se_t0, t_t0, p_t0, cilo_t0, cihi_t0, sig_t0 = _extract(flood_col_t0)
    b_t1, se_t1, t_t1, p_t1, cilo_t1, cihi_t1, sig_t1 = _extract(flood_col_t1)
    b_t2, se_t2, t_t2, p_t2, cilo_t2, cihi_t2, sig_t2 = _extract(flood_col_t2)

    nobs = int(result.nobs)
    r2_w = result.rsquared

    def _print_lag(tag, b, se, t, p, cilo, cihi, sig):
        print(f"\n    [{tag}]")
        print(f"      beta    = {b:.6f}")
        print(f"      SE      = {se:.6f}")
        print(f"      t       = {t:.4f}")
        print(f"      p       = {p:.6f}  {sig if sig else '(NOT SIGNIFICANT)'}")
        print(f"      95% CI  = [{cilo:.6f}, {cihi:.6f}]")

    def _log_lag(tag, b, se, t, p, cilo, cihi, sig, anchor_b):
        log.info(f"    [{tag}]")
        log.info(f"      beta = {b:.6f}  (anchor: {anchor_b})")
        log.info(f"      SE   = {se:.6f}")
        log.info(f"      t    = {t:.4f}")
        log.info(f"      p    = {p:.6f}  {sig if sig else '(NOT SIGNIFICANT)'}")
        log.info(f"      95% CI = [{cilo:.6f}, {cihi:.6f}]")

    print(f"\n  Rule {rule_label}:")
    print(f"    N = {nobs:,} | R2(within/time) = {r2_w:.4f}")
    _print_lag("t0  Current quarter", b_t0, se_t0, t_t0, p_t0, cilo_t0, cihi_t0, sig_t0)
    _print_lag("t-1 One quarter lag", b_t1, se_t1, t_t1, p_t1, cilo_t1, cihi_t1, sig_t1)
    _print_lag("t-2 Two quarter lag", b_t2, se_t2, t_t2, p_t2, cilo_t2, cihi_t2, sig_t2)

    log.info(f"    N = {nobs:,}, R2(within/time) = {r2_w:.4f}")
    _log_lag("t0  Current quarter", b_t0, se_t0, t_t0, p_t0, cilo_t0, cihi_t0, sig_t0,
             f"{anchor_t0:.6f}" if not np.isnan(anchor_t0) else "not anchored")
    _log_lag("t-1 One quarter lag", b_t1, se_t1, t_t1, p_t1, cilo_t1, cihi_t1, sig_t1,
             f"{anchor_t1:.6f}" if not np.isnan(anchor_t1) else "not anchored")
    _log_lag("t-2 Two quarter lag", b_t2, se_t2, t_t2, p_t2, cilo_t2, cihi_t2, sig_t2,
             f"{anchor_t2:.6f}" if not np.isnan(anchor_t2) else "not anchored")

    # Stability check: only apply where anchor is numerically confirmed.
    for tag, b, anchor in [
        ("t0",  b_t0, anchor_t0),
        ("t-1", b_t1, anchor_t1),
        ("t-2", b_t2, anchor_t2)
    ]:
        if np.isnan(anchor):
            print(f"    Stability Rule {rule_label} {tag}: anchor not confirmed -- SKIP")
            log.info(f"    Stability Rule {rule_label} {tag}: anchor not confirmed -- SKIP")
        else:
            delta = abs(b - anchor)
            if delta > STABILITY_THRESHOLD:
                msg = (
                    f"STABILITY WARNING Rule {rule_label} {tag}: "
                    f"|beta_29b - beta_29| = {delta:.6f} > threshold {STABILITY_THRESHOLD}. "
                    f"Investigate before writing. Do not proceed to paper tables."
                )
                print(f"    *** {msg}")
                log.info(f"    *** {msg}")
            else:
                stability_msg = (
                    f"Coefficient stable Rule {rule_label} {tag}: "
                    f"delta = {delta:.6f} <= threshold {STABILITY_THRESHOLD} -- PASS"
                )
                print(f"    {stability_msg}")
                log.info(f"    {stability_msg}")

    return (result,
            b_t0, se_t0, t_t0, p_t0, cilo_t0, cihi_t0, sig_t0,
            b_t1, se_t1, t_t1, p_t1, cilo_t1, cihi_t1, sig_t1,
            b_t2, se_t2, t_t2, p_t2, cilo_t2, cihi_t2, sig_t2,
            nobs, r2_w)

(result_A,
 bA_t0, seA_t0, tA_t0, pA_t0, ciloA_t0, cihiA_t0, sigA_t0,
 bA_t1, seA_t1, tA_t1, pA_t1, ciloA_t1, cihiA_t1, sigA_t1,
 bA_t2, seA_t2, tA_t2, pA_t2, ciloA_t2, cihiA_t2, sigA_t2,
 n_A, r2_A) = fit_h3(
    df_A,
    'flood_exposure_ruleA_qt', 'flood_ruleA_L1', 'flood_ruleA_L2',
    'A', quarters_A,
    ANCHOR_A_T0_BETA, ANCHOR_A_T1_BETA, ANCHOR_A_T2_BETA
)

(result_B,
 bB_t0, seB_t0, tB_t0, pB_t0, ciloB_t0, cihiB_t0, sigB_t0,
 bB_t1, seB_t1, tB_t1, pB_t1, ciloB_t1, cihiB_t1, sigB_t1,
 bB_t2, seB_t2, tB_t2, pB_t2, ciloB_t2, cihiB_t2, sigB_t2,
 n_B, r2_B) = fit_h3(
    df_B,
    'flood_exposure_ruleB_qt', 'flood_ruleB_L1', 'flood_ruleB_L2',
    'B', quarters_B,
    ANCHOR_B_T0_BETA, ANCHOR_B_T1_BETA, ANCHOR_B_T2_BETA
)

# =============================================================================
# [6/7] SIDE-BY-SIDE SUMMARY AND CONSISTENCY CHECKS
# =============================================================================

print("\n" + "=" * 70)
print("H3 RESULTS SUMMARY -- linearmodels PanelOLS (time FE only)")
print("=" * 70)
print(f"  Dependent: deposit_change_qt")
print(f"  FE: Quarter only (time_effects=True, entity_effects=False)")
print(f"  SE: Clustered by entity (district_state_id, 631 clusters)")
print(f"  {'Lag':<6} {'Rule':<6} {'Beta':>12} {'SE':>10} {'t':>8} {'p':>10} {'Sig':>5}")
print(f"  {'-' * 60}")

for (lag, bA, sA, tA, pA, sgA, bB, sB, tB, pB, sgB) in [
    ("t0",  bA_t0, seA_t0, tA_t0, pA_t0, sigA_t0,
             bB_t0, seB_t0, tB_t0, pB_t0, sigB_t0),
    ("t-1", bA_t1, seA_t1, tA_t1, pA_t1, sigA_t1,
             bB_t1, seB_t1, tB_t1, pB_t1, sigB_t1),
    ("t-2", bA_t2, seA_t2, tA_t2, pA_t2, sigA_t2,
             bB_t2, seB_t2, tB_t2, pB_t2, sigB_t2),
]:
    print(f"  {lag:<6} {'A':<6} {bA:>12.6f} {sA:>10.6f} {tA:>8.4f} {pA:>10.6f} {sgA:>5}")
    print(f"  {lag:<6} {'B':<6} {bB:>12.6f} {sB:>10.6f} {tB:>8.4f} {pB:>10.6f} {sgB:>5}")
    print(f"  {'-' * 60}")

print(f"  N (Rule A): {n_A:,} | N (Rule B): {n_B:,}")
print(f"  Quarter FE: {len(quarters_A)} | District FE: NONE (pre-committed)")
print()
print(f"  Script 29 anchors (statsmodels):")
print(f"  {'t0':<6} {'A':<6} {ANCHOR_A_T0_BETA:>12.6f} {ANCHOR_A_T0_SE:>10.6f}  p=0.677")
print(f"  {'t-1':<6} {'A':<6} {ANCHOR_A_T1_BETA:>12.6f} {ANCHOR_A_T1_SE:>10.6f}  p=0.177")
print(f"  {'t-2':<6} {'A':<6} {ANCHOR_A_T2_BETA:>12.6f} {ANCHOR_A_T2_SE:>10.6f}  p<0.001 ***")

log.info("\n" + "=" * 70)
log.info("SIDE-BY-SIDE SUMMARY -- linearmodels PanelOLS (time FE only)")
log.info("=" * 70)
log.info(f"  {'Lag':<6} {'Rule':<6} {'Beta':>12} {'SE':>10} {'t':>8} {'p':>10} {'Sig':>5}")
log.info(f"  {'-' * 60}")
for (lag, bA, sA, tA, pA, sgA, bB, sB, tB, pB, sgB) in [
    ("t0",  bA_t0, seA_t0, tA_t0, pA_t0, sigA_t0,
             bB_t0, seB_t0, tB_t0, pB_t0, sigB_t0),
    ("t-1", bA_t1, seA_t1, tA_t1, pA_t1, sigA_t1,
             bB_t1, seB_t1, tB_t1, pB_t1, sigB_t1),
    ("t-2", bA_t2, seA_t2, tA_t2, pA_t2, sigA_t2,
             bB_t2, seB_t2, tB_t2, pB_t2, sigB_t2),
]:
    log.info(f"  {lag:<6} {'A':<6} {bA:>12.6f} {sA:>10.6f} {tA:>8.4f} {pA:>10.6f} {sgA:>5}")
    log.info(f"  {lag:<6} {'B':<6} {bB:>12.6f} {sB:>10.6f} {tB:>8.4f} {pB:>10.6f} {sgB:>5}")
    log.info(f"  {'-' * 60}")
log.info(f"  N (Rule A): {n_A:,} | N (Rule B): {n_B:,}")
log.info(f"  Quarter FE: {len(quarters_A)} | District FE: NONE (pre-committed)")

# H3 key result check: t-2 Rule A must be negative and significant.
if pA_t2 < 0.001 and bA_t2 < 0:
    log.info(f"  H3 CONFIRMED: Rule A t-2 negative and p<0.001 -- PASS")
elif pA_t2 < 0.05 and bA_t2 < 0:
    log.info(f"  H3 CONFIRMED: Rule A t-2 negative and p={pA_t2:.4f} < 0.05 -- PASS")
else:
    log.info(
        f"  H3 WARNING: Rule A t-2 result unexpected. "
        f"beta={bA_t2:.6f}, p={pA_t2:.4f}. "
        f"Investigate before writing."
    )

# Sign checks for t0 and t-1 Rule A (expected null; log actual direction).
for lag_label, b, p in [("t0",  bA_t0, pA_t0), ("t-1", bA_t1, pA_t1)]:
    direction = "positive" if b > 0 else "negative"
    sig_label = "significant" if p < 0.05 else "null"
    log.info(f"  Rule A {lag_label}: {direction}, {sig_label} (p={p:.4f}) -- expected null")

# =============================================================================
# [7/7] SAVE OUTPUTS
# =============================================================================

print("\n[7/7] Saving outputs...")
log.info("\n[7/7] Saving outputs")

rows = []
rule_specs = [
    ('A', result_A,
     ['flood_exposure_ruleA_qt', 'flood_ruleA_L1', 'flood_ruleA_L2'],
     [bA_t0, bA_t1, bA_t2],
     [seA_t0, seA_t1, seA_t2],
     [tA_t0, tA_t1, tA_t2],
     [pA_t0, pA_t1, pA_t2],
     [ciloA_t0, ciloA_t1, ciloA_t2],
     [cihiA_t0, cihiA_t1, cihiA_t2],
     [sigA_t0, sigA_t1, sigA_t2],
     [ANCHOR_A_T0_BETA, ANCHOR_A_T1_BETA, ANCHOR_A_T2_BETA],
     [ANCHOR_A_T0_SE,   ANCHOR_A_T1_SE,   ANCHOR_A_T2_SE],
     n_A, r2_A, len(quarters_A),
     ('Primary. Quarter FE only (pre-committed). '
      'H3 CONFIRMED at t-2 (beta=-0.007005, p<0.001). '
      'Two-phase cycle: t-1 positive (anticipatory saving), t-2 negative (withdrawal). '
      'Writing constraint 11 applies -- disclose two-phase cycle in full.')),
    ('B', result_B,
     ['flood_exposure_ruleB_qt', 'flood_ruleB_L1', 'flood_ruleB_L2'],
     [bB_t0, bB_t1, bB_t2],
     [seB_t0, seB_t1, seB_t2],
     [tB_t0, tB_t1, tB_t2],
     [pB_t0, pB_t1, pB_t2],
     [ciloB_t0, ciloB_t1, ciloB_t2],
     [cihiB_t0, cihiB_t1, cihiB_t2],
     [sigB_t0, sigB_t1, sigB_t2],
     [ANCHOR_B_T0_BETA, ANCHOR_B_T1_BETA, ANCHOR_B_T2_BETA],
     [np.nan, np.nan, np.nan],
     n_B, r2_B, len(quarters_B),
     'Robustness. District-only match. 0.90% treatment rate. All lags null -- expected.')
]

lag_labels = ['t0', 't-1', 't-2']

for (rule, result_obj, var_names, betas, ses, tstats, pvals,
     cilos, cihis, sigs, anchor_betas, anchor_ses,
     nobs, r2, n_qfe, note) in rule_specs:
    for i in range(3):
        ab = anchor_betas[i]
        delta = round(abs(betas[i] - ab), 6) if not np.isnan(ab) else np.nan
        rows.append({
            'hypothesis'              : 'H3',
            'rule'                    : rule,
            'lag'                     : lag_labels[i],
            'estimator'               : 'linearmodels.PanelOLS',
            'specification'           : (
                'deposit_change_qt ~ flood_L0 + flood_L1 + flood_L2 + TimeFE'
            ),
            'variable'                : var_names[i],
            'coefficient'             : round(betas[i],  6),
            'std_error'               : round(ses[i],    6),
            't_statistic'             : round(tstats[i], 4),
            'p_value'                 : round(pvals[i],  6),
            'ci_lower_95'             : round(cilos[i],  6),
            'ci_upper_95'             : round(cihis[i],  6),
            'n_obs'                   : nobs,
            'r_squared_within_time'   : round(r2,        4),
            'time_fe'                 : 'quarter',
            'n_time_fe'               : n_qfe,
            'entity_fe'               : 'NONE (pre-committed H3 specification)',
            'se_type'                 : 'clustered_entity (district_state_id, 631 clusters)',
            'significance'            : sigs[i],
            'anchor_beta_script29'    : round(ab, 6) if not np.isnan(ab) else np.nan,
            'anchor_se_script29'      : (round(anchor_ses[i], 6)
                                         if not np.isnan(anchor_ses[i]) else np.nan),
            'delta_beta'              : delta,
            'note'                    : note
        })

OUTPUT_CSV = '05_Outputs/Tables/04b_H3_linearmodels.csv'
results_df = pd.DataFrame(rows)
results_df.to_csv(OUTPUT_CSV, index=False)
assert os.path.exists(OUTPUT_CSV), f"CSV not written: {OUTPUT_CSV}"
print(f"  CSV saved: {OUTPUT_CSV} -- PASS")
log.info(f"  CSV saved: {OUTPUT_CSV} -- PASS")

OUTPUT_SUMMARY_A = '05_Outputs/Logs/29b_H3_linearmodels_full_ruleA.txt'
OUTPUT_SUMMARY_B = '05_Outputs/Logs/29b_H3_linearmodels_full_ruleB.txt'

with open(OUTPUT_SUMMARY_A, 'w') as f:
    f.write(str(result_A.summary))
assert os.path.exists(OUTPUT_SUMMARY_A)
print(f"  Full summary (Rule A): {OUTPUT_SUMMARY_A} -- PASS")
log.info(f"  Full summary (Rule A): {OUTPUT_SUMMARY_A} -- PASS")

with open(OUTPUT_SUMMARY_B, 'w') as f:
    f.write(str(result_B.summary))
assert os.path.exists(OUTPUT_SUMMARY_B)
print(f"  Full summary (Rule B): {OUTPUT_SUMMARY_B} -- PASS")
log.info(f"  Full summary (Rule B): {OUTPUT_SUMMARY_B} -- PASS")

print("\n" + "=" * 70)
print("SCRIPT 29b COMPLETE")
print("=" * 70)
print(f"  CSV:           {OUTPUT_CSV}")
print(f"  Log:           05_Outputs/Logs/29b_H3_linearmodels.txt")
print(f"  Full (Rule A): {OUTPUT_SUMMARY_A}")
print(f"  Full (Rule B): {OUTPUT_SUMMARY_B}")
print("=" * 70)
print("NEXT STEP: Run Script 30b (H4: Heterogeneity -- linearmodels PanelOLS)")
print("=" * 70)

log.info("\n" + "=" * 70)
log.info("SCRIPT 29b COMPLETE")
log.info(f"  CSV:           {OUTPUT_CSV}")
log.info(f"  Full (Rule A): {OUTPUT_SUMMARY_A}")
log.info(f"  Full (Rule B): {OUTPUT_SUMMARY_B}")
log.info("Next: Script 30b -- H4 Heterogeneity linearmodels PanelOLS")
log.info("=" * 70)
