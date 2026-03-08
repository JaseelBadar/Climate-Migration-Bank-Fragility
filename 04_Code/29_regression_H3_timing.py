"""
29_regression_H3_timing.py
H3: Distributed Lag -- Flood Timing -> Deposit Withdrawals
Tests whether flood-induced deposit stress is immediate, 1Q lagged, or 2Q lagged.

PRE-COMMITTED SPECIFICATION: Quarter FE only. NO district FE.
Rationale: deposit_change_qt is log-differenced -- district-level trends
absorbed by differencing. District FE in a differenced spec is not part of
the pre-committed H3 design (Hypotheses v2.4, Section H3a). This is also
why H3 was validated as clean -- unaffected by any pipeline contamination
event (no VIIRS, no district FE, no homonymous FE collapse).

Uses pre-computed lag columns from Script 24:
  flood_ruleA_L1, flood_ruleA_L2 (Rule A lags)
  flood_ruleB_L1, flood_ruleB_L2 (Rule B lags)
Both Rule A (primary) and Rule B (robustness) estimated.
SE: Clustered by district_state_id throughout.
"""

import pandas as pd
import numpy as np
from statsmodels.formula.api import ols
import logging
import os


# === SETUP ===
os.makedirs('05_Outputs/Logs', exist_ok=True)
os.makedirs('05_Outputs/Tables', exist_ok=True)

logging.basicConfig(
    filename='05_Outputs/Logs/29_H3_regression.txt',
    level=logging.INFO,
    format='%(message)s',
    filemode='w'
)
log = logging.getLogger(__name__)


print("=" * 70)
print("PHASE 4: H3 DISTRIBUTED LAG REGRESSION (Floods -> Deposits, Timing)")
print("=" * 70)
log.info("=" * 70)
log.info("H3: DISTRIBUTED LAG REGRESSION")
log.info("Flood Timing -> Deposit Withdrawals")
log.info("SPECIFICATION: Quarter FE only (NO district FE) -- pre-committed")
log.info("=" * 70)


# =============================================================================
# STEP 1: LOAD DATA
# =============================================================================
print("\n[1/6] Loading regression-ready panel...")
df = pd.read_csv('03_Data_Clean/regression_panel_final.csv')
assert len(df) == 23347, f"Expected 23,347 rows, got {len(df):,}"
assert df.shape[1] == 23,  f"Expected 23 columns, got {df.shape[1]}"
print(f"  Loaded: {len(df):,} rows, {df.shape[1]} columns -- PASS")
log.info(f"\nPanel loaded: {len(df):,} rows, {df.shape[1]} columns")


# === REQUIRED COLUMNS ===
required_cols = [
    'deposit_change_qt',
    'flood_exposure_ruleA_qt', 'flood_ruleA_L1', 'flood_ruleA_L2',
    'flood_exposure_ruleB_qt', 'flood_ruleB_L1', 'flood_ruleB_L2',
    'district_gadm', 'state_gadm', 'quarter'
]
missing_cols = [c for c in required_cols if c not in df.columns]
if missing_cols:
    raise ValueError(f"Missing required columns: {missing_cols}")
print(f"  Required columns verified -- PASS")
log.info(f"Required columns verified -- PASS")


# =============================================================================
# STEP 2: COMPOSITE KEY (for clustering)
# =============================================================================
print("\n[2/6] Constructing composite key...")

# CRITICAL: composite key prevents 7 homonymous pairs from collapsing in clustering.
# district_gadm alone -> 624 unique (WRONG). Composite -> 631 (CORRECT).
# Note: district FE is NOT used in H3 regressions (pre-committed).
# Composite key is used for clustered SE grouping only.
df['district_state_id'] = df['district_gadm'] + '_' + df['state_gadm']
n_districts = df['district_state_id'].nunique()
print(f"  district_state_id: {n_districts} unique pairs  (expected 631)")
log.info(f"\ndistrict_state_id: {n_districts} unique pairs  (expected 631)")

if n_districts != 631:
    raise ValueError(
        f"District count {n_districts} != 631. "
        f"Check composite key construction or upstream pipeline."
    )
print(f"  Composite key verified -- PASS")
log.info("Composite key verified -- PASS")


# =============================================================================
# STEP 3: VERIFY PRE-COMPUTED LAG ARITHMETIC
# =============================================================================
print("\n[3/6] Verifying pre-computed lag arithmetic (Script 24 output)...")

nan_ruleA_L0 = df['flood_exposure_ruleA_qt'].isna().sum()
nan_ruleA_L1 = df['flood_ruleA_L1'].isna().sum()
nan_ruleA_L2 = df['flood_ruleA_L2'].isna().sum()
nan_ruleB_L0 = df['flood_exposure_ruleB_qt'].isna().sum()
nan_ruleB_L1 = df['flood_ruleB_L1'].isna().sum()
nan_ruleB_L2 = df['flood_ruleB_L2'].isna().sum()

print(f"  flood_ruleA  L0 NaN: {nan_ruleA_L0}      (expected 0)")
print(f"  flood_ruleA  L1 NaN: {nan_ruleA_L1}    (expected 631)")
print(f"  flood_ruleA  L2 NaN: {nan_ruleA_L2}  (expected 1,262)")
print(f"  flood_ruleB  L0 NaN: {nan_ruleB_L0}      (expected 0)")
print(f"  flood_ruleB  L1 NaN: {nan_ruleB_L1}    (expected 631)")
print(f"  flood_ruleB  L2 NaN: {nan_ruleB_L2}  (expected 1,262)")

log.info(f"\nLag NaN arithmetic (from Script 24 pre-computed columns):")
log.info(f"  flood_ruleA L0 NaN: {nan_ruleA_L0}     (expected 0)")
log.info(f"  flood_ruleA L1 NaN: {nan_ruleA_L1}   (expected 631)")
log.info(f"  flood_ruleA L2 NaN: {nan_ruleA_L2} (expected 1,262)")
log.info(f"  flood_ruleB L0 NaN: {nan_ruleB_L0}     (expected 0)")
log.info(f"  flood_ruleB L1 NaN: {nan_ruleB_L1}   (expected 631)")
log.info(f"  flood_ruleB L2 NaN: {nan_ruleB_L2} (expected 1,262)")

if nan_ruleA_L1 != 631:
    raise ValueError(f"Rule A L1 NaN = {nan_ruleA_L1}, expected 631. Check Script 24.")
if nan_ruleA_L2 != 1262:
    raise ValueError(f"Rule A L2 NaN = {nan_ruleA_L2}, expected 1,262. Check Script 24.")
if nan_ruleB_L1 != 631:
    raise ValueError(f"Rule B L1 NaN = {nan_ruleB_L1}, expected 631. Check Script 24.")
if nan_ruleB_L2 != 1262:
    raise ValueError(f"Rule B L2 NaN = {nan_ruleB_L2}, expected 1,262. Check Script 24.")

print(f"  Lag arithmetic verified -- PASS")
log.info("Lag arithmetic verified -- PASS")


# =============================================================================
# STEP 4: RESTRICT TO COMPLETE CASES
# =============================================================================
print("\n[4/6] Restricting to complete cases...")
initial_n = len(df)

# Rule A: deposit + flood L0/L1/L2 all non-missing
df_A = df[
    df['deposit_change_qt'].notna()      &
    df['flood_exposure_ruleA_qt'].notna() &
    df['flood_ruleA_L1'].notna()          &
    df['flood_ruleA_L2'].notna()
].copy()

# Rule B: deposit + flood L0/L1/L2 all non-missing
df_B = df[
    df['deposit_change_qt'].notna()      &
    df['flood_exposure_ruleB_qt'].notna() &
    df['flood_ruleB_L1'].notna()          &
    df['flood_ruleB_L2'].notna()
].copy()

dropped_A = initial_n - len(df_A)
dropped_B = initial_n - len(df_B)

print(f"  Initial:               {initial_n:,} obs")
print(f"  After restriction (A): {len(df_A):,} obs  (expected ~21,180)")
print(f"  After restriction (B): {len(df_B):,} obs  (expected ~21,180)")
print(f"  Dropped (A):           {dropped_A:,} obs ({dropped_A / initial_n * 100:.1f}%)")
print(f"  Dropped (B):           {dropped_B:,} obs ({dropped_B / initial_n * 100:.1f}%)")

log.info(f"\nInitial: {initial_n:,} obs")
log.info(f"After restriction (Rule A): {len(df_A):,} obs  (expected ~21,180)")
log.info(f"After restriction (Rule B): {len(df_B):,} obs  (expected ~21,180)")
log.info(f"Dropped (Rule A): {dropped_A:,} ({dropped_A / initial_n * 100:.1f}%)")
log.info(f"Dropped (Rule B): {dropped_B:,} ({dropped_B / initial_n * 100:.1f}%)")
log.info(f"Drop breakdown (Rule A): 631x2=1,262 lag NaN + {dropped_A - 1262} additional deposit NaN")


# =============================================================================
# STEP 5: ENCODE QUARTER FE
# =============================================================================
print("\n[5/6] Encoding quarter FE (no district FE -- pre-committed)...")

df_A['quarter_fe'] = pd.Categorical(df_A['quarter'])
df_B['quarter_fe'] = pd.Categorical(df_B['quarter'])

n_qfe_A = df_A['quarter_fe'].nunique()
n_qfe_B = df_B['quarter_fe'].nunique()

print(f"  Rule A quarter FE: {n_qfe_A}  (expected 36)")
print(f"  Rule B quarter FE: {n_qfe_B}  (expected 36)")
log.info(f"\nQuarter FE (Rule A): {n_qfe_A}  (expected 36)")
log.info(f"Quarter FE (Rule B): {n_qfe_B}  (expected 36)")

if n_qfe_A < 33 or n_qfe_A > 38:
    raise ValueError(f"Quarter FE count {n_qfe_A} outside expected range [33, 38].")

print(f"  Quarter FE verified -- PASS")
log.info("Quarter FE verified -- PASS")


# === HELPER: EXTRACT COEFFICIENT ROW ===
def extract_coef(model, varname):
    coef  = model.params.get(varname, np.nan)
    se    = model.bse.get(varname, np.nan)
    tstat = model.tvalues.get(varname, np.nan)
    pval  = model.pvalues.get(varname, np.nan)
    ci    = model.conf_int()
    ci_lo = ci.loc[varname, 0] if varname in ci.index else np.nan
    ci_hi = ci.loc[varname, 1] if varname in ci.index else np.nan
    if pval < 0.01:   sig = "***"
    elif pval < 0.05: sig = "**"
    elif pval < 0.10: sig = "*"
    else:             sig = ""
    return coef, se, tstat, pval, ci_lo, ci_hi, sig


def print_lag(label, coef, se, tstat, pval, ci_lo, ci_hi, sig):
    print(f"\n    [{label}]")
    print(f"      Beta    = {coef:.6f}")
    print(f"      SE      = {se:.6f}")
    print(f"      t       = {tstat:.3f}")
    print(f"      p       = {pval:.6f}")
    print(f"      95% CI  = [{ci_lo:.6f}, {ci_hi:.6f}]")
    print(f"      Status  = {sig if sig else 'NOT SIGNIFICANT'}")


def log_lag(label, coef, se, tstat, pval, ci_lo, ci_hi, sig):
    log.info(f"\n  [{label}]")
    log.info(f"    Beta    = {coef:.6f}")
    log.info(f"    SE      = {se:.6f}")
    log.info(f"    t       = {tstat:.3f}")
    log.info(f"    p       = {pval:.6f}")
    log.info(f"    95% CI  = [{ci_lo:.6f}, {ci_hi:.6f}]")
    log.info(f"    Status  = {sig if sig else 'NOT SIGNIFICANT'}")


# =============================================================================
# RULE A: PRIMARY SPECIFICATION
# =============================================================================
print("\n[5a/6] Rule A: OLS, quarter FE, clustered SE...")
log.info("\n" + "=" * 70)
log.info("RULE A: PRIMARY SPECIFICATION")
log.info("=" * 70)
log.info("Dependent:   deposit_change_qt")
log.info("Regressors:  flood_exposure_ruleA_qt (t0)")
log.info("             flood_ruleA_L1          (t-1)")
log.info("             flood_ruleA_L2          (t-2)")
log.info("FE:          Quarter only (NO district FE -- pre-committed H3 design)")
log.info("SE:          Clustered by district_state_id")
log.info("Expected:    t0 and/or t-1 < 0, attenuation by t-2")
log.info("Validated:   Feb 6 t-2 beta=-0.0091, p=0.012 (clean spec, N=21,912)")

formula_A = ('deposit_change_qt ~ flood_exposure_ruleA_qt + '
             'flood_ruleA_L1 + flood_ruleA_L2 + C(quarter_fe)')

try:
    model_A = ols(formula_A, data=df_A).fit(
        cov_type='cluster',
        cov_kwds={'groups': df_A['district_state_id']}
    )
    print(f"  Model fitted -- PASS")
    print(f"  N obs:  {model_A.nobs:,.0f}")
    print(f"  R2:     {model_A.rsquared:.4f}")
    print(f"  R2-adj: {model_A.rsquared_adj:.4f}")
    log.info(f"\nModel fitted: N={model_A.nobs:,.0f}, R2={model_A.rsquared:.4f}, "
             f"R2-adj={model_A.rsquared_adj:.4f}")
except Exception as e:
    log.error(f"Rule A model fitting failed: {e}")
    raise

coef_A_t0, se_A_t0, t_A_t0, p_A_t0, cilo_A_t0, cihi_A_t0, sig_A_t0 = extract_coef(model_A, 'flood_exposure_ruleA_qt')
coef_A_t1, se_A_t1, t_A_t1, p_A_t1, cilo_A_t1, cihi_A_t1, sig_A_t1 = extract_coef(model_A, 'flood_ruleA_L1')
coef_A_t2, se_A_t2, t_A_t2, p_A_t2, cilo_A_t2, cihi_A_t2, sig_A_t2 = extract_coef(model_A, 'flood_ruleA_L2')

print_lag("t0  Current quarter", coef_A_t0, se_A_t0, t_A_t0, p_A_t0, cilo_A_t0, cihi_A_t0, sig_A_t0)
print_lag("t-1 One quarter lag", coef_A_t1, se_A_t1, t_A_t1, p_A_t1, cilo_A_t1, cihi_A_t1, sig_A_t1)
print_lag("t-2 Two quarter lag", coef_A_t2, se_A_t2, t_A_t2, p_A_t2, cilo_A_t2, cihi_A_t2, sig_A_t2)

log.info("\nRESULTS (Rule A):")
log_lag("t0  Current quarter", coef_A_t0, se_A_t0, t_A_t0, p_A_t0, cilo_A_t0, cihi_A_t0, sig_A_t0)
log_lag("t-1 One quarter lag", coef_A_t1, se_A_t1, t_A_t1, p_A_t1, cilo_A_t1, cihi_A_t1, sig_A_t1)
log_lag("t-2 Two quarter lag", coef_A_t2, se_A_t2, t_A_t2, p_A_t2, cilo_A_t2, cihi_A_t2, sig_A_t2)

log.info("\nINTERPRETATION (pre-committed, not post-hoc):")
log.info("  Expected pattern: t0 and/or t-1 negative, attenuation by t-2.")
log.info(f"  t0:  {'negative' if coef_A_t0 < 0 else 'positive'} ({coef_A_t0:.6f}), p={p_A_t0:.4f}")
log.info(f"  t-1: {'negative' if coef_A_t1 < 0 else 'positive'} ({coef_A_t1:.6f}), p={p_A_t1:.4f}")
log.info(f"  t-2: {'negative' if coef_A_t2 < 0 else 'positive'} ({coef_A_t2:.6f}), p={p_A_t2:.4f}")
if (p_A_t0 < 0.05 and coef_A_t0 < 0) or (p_A_t1 < 0.05 and coef_A_t1 < 0) or (p_A_t2 < 0.05 and coef_A_t2 < 0):
    log.info("  Conclusion: H3 SUPPORTED. At least one lag negative and significant.")
    log.info("  Liquidity timeline: deposit stress within 2 quarters of flood.")
else:
    log.info("  Conclusion: H3 NOT SUPPORTED. No lag significant at 5% level.")
    log.info("  Mechanism does not operate through deposit channel at 0-2Q horizon.")


# =============================================================================
# RULE B: ROBUSTNESS SPECIFICATION
# =============================================================================
print("\n[5b/6] Rule B: OLS, quarter FE, clustered SE...")
log.info("\n" + "=" * 70)
log.info("RULE B: ROBUSTNESS SPECIFICATION")
log.info("=" * 70)
log.info("Regressors:  flood_exposure_ruleB_qt + flood_ruleB_L1 + flood_ruleB_L2")
log.info("FE:          Quarter only | SE: Clustered district_state_id")
log.info("Note:        Rule B district-only match. Higher precision, lower power.")

formula_B = ('deposit_change_qt ~ flood_exposure_ruleB_qt + '
             'flood_ruleB_L1 + flood_ruleB_L2 + C(quarter_fe)')

try:
    model_B = ols(formula_B, data=df_B).fit(
        cov_type='cluster',
        cov_kwds={'groups': df_B['district_state_id']}
    )
    print(f"  Model fitted -- PASS")
    print(f"  N obs:  {model_B.nobs:,.0f}")
    print(f"  R2:     {model_B.rsquared:.4f}")
    print(f"  R2-adj: {model_B.rsquared_adj:.4f}")
    log.info(f"\nModel fitted: N={model_B.nobs:,.0f}, R2={model_B.rsquared:.4f}, "
             f"R2-adj={model_B.rsquared_adj:.4f}")
except Exception as e:
    log.error(f"Rule B model fitting failed: {e}")
    raise

coef_B_t0, se_B_t0, t_B_t0, p_B_t0, cilo_B_t0, cihi_B_t0, sig_B_t0 = extract_coef(model_B, 'flood_exposure_ruleB_qt')
coef_B_t1, se_B_t1, t_B_t1, p_B_t1, cilo_B_t1, cihi_B_t1, sig_B_t1 = extract_coef(model_B, 'flood_ruleB_L1')
coef_B_t2, se_B_t2, t_B_t2, p_B_t2, cilo_B_t2, cihi_B_t2, sig_B_t2 = extract_coef(model_B, 'flood_ruleB_L2')

print_lag("t0  Current quarter", coef_B_t0, se_B_t0, t_B_t0, p_B_t0, cilo_B_t0, cihi_B_t0, sig_B_t0)
print_lag("t-1 One quarter lag", coef_B_t1, se_B_t1, t_B_t1, p_B_t1, cilo_B_t1, cihi_B_t1, sig_B_t1)
print_lag("t-2 Two quarter lag", coef_B_t2, se_B_t2, t_B_t2, p_B_t2, cilo_B_t2, cihi_B_t2, sig_B_t2)

log.info("\nRESULTS (Rule B):")
log_lag("t0  Current quarter", coef_B_t0, se_B_t0, t_B_t0, p_B_t0, cilo_B_t0, cihi_B_t0, sig_B_t0)
log_lag("t-1 One quarter lag", coef_B_t1, se_B_t1, t_B_t1, p_B_t1, cilo_B_t1, cihi_B_t1, sig_B_t1)
log_lag("t-2 Two quarter lag", coef_B_t2, se_B_t2, t_B_t2, p_B_t2, cilo_B_t2, cihi_B_t2, sig_B_t2)


# =============================================================================
# SIDE-BY-SIDE SUMMARY
# =============================================================================
print("\n" + "=" * 70)
print("H3 RESULTS SUMMARY")
print("=" * 70)
print(f"  Dependent: deposit_change_qt")
print(f"  FE: Quarter only (NO district FE) | SE: Clustered district_state_id")
print(f"  {'Lag':<6} {'Rule':<6} {'Beta':>12} {'SE':>10} {'t':>8} {'p':>10} {'Sig':>5}")
print(f"  {'-'*60}")
for lag, cA, sA, tA, pA, sgA, cB, sB, tB, pB, sgB in [
    ("t0",  coef_A_t0, se_A_t0, t_A_t0, p_A_t0, sig_A_t0,
             coef_B_t0, se_B_t0, t_B_t0, p_B_t0, sig_B_t0),
    ("t-1", coef_A_t1, se_A_t1, t_A_t1, p_A_t1, sig_A_t1,
             coef_B_t1, se_B_t1, t_B_t1, p_B_t1, sig_B_t1),
    ("t-2", coef_A_t2, se_A_t2, t_A_t2, p_A_t2, sig_A_t2,
             coef_B_t2, se_B_t2, t_B_t2, p_B_t2, sig_B_t2),
]:
    print(f"  {lag:<6} {'A':<6} {cA:>12.6f} {sA:>10.6f} {tA:>8.3f} {pA:>10.6f} {sgA:>5}")
    print(f"  {lag:<6} {'B':<6} {cB:>12.6f} {sB:>10.6f} {tB:>8.3f} {pB:>10.6f} {sgB:>5}")
    print(f"  {'-'*60}")
print(f"  N (Rule A): {model_A.nobs:,.0f} | N (Rule B): {model_B.nobs:,.0f}")
print(f"  Quarter FE: {n_qfe_A} | District FE: NONE (pre-committed)")

log.info("\n" + "=" * 70)
log.info("SIDE-BY-SIDE SUMMARY")
log.info("=" * 70)
log.info(f"  {'Lag':<6} {'Rule':<6} {'Beta':>12} {'SE':>10} {'t':>8} {'p':>10} {'Sig':>5}")
log.info(f"  {'-'*60}")
for lag, cA, sA, tA, pA, sgA, cB, sB, tB, pB, sgB in [
    ("t0",  coef_A_t0, se_A_t0, t_A_t0, p_A_t0, sig_A_t0,
             coef_B_t0, se_B_t0, t_B_t0, p_B_t0, sig_B_t0),
    ("t-1", coef_A_t1, se_A_t1, t_A_t1, p_A_t1, sig_A_t1,
             coef_B_t1, se_B_t1, t_B_t1, p_B_t1, sig_B_t1),
    ("t-2", coef_A_t2, se_A_t2, t_A_t2, p_A_t2, sig_A_t2,
             coef_B_t2, se_B_t2, t_B_t2, p_B_t2, sig_B_t2),
]:
    log.info(f"  {lag:<6} {'A':<6} {cA:>12.6f} {sA:>10.6f} {tA:>8.3f} {pA:>10.6f} {sgA:>5}")
    log.info(f"  {lag:<6} {'B':<6} {cB:>12.6f} {sB:>10.6f} {tB:>8.3f} {pB:>10.6f} {sgB:>5}")
    log.info(f"  {'-'*60}")
log.info(f"  N (Rule A): {model_A.nobs:,.0f} | N (Rule B): {model_B.nobs:,.0f}")
log.info(f"  Quarter FE: {n_qfe_A} | District FE: NONE (pre-committed)")


# =============================================================================
# STEP 6: SAVE OUTPUTS
# =============================================================================
print("\n[6/6] Saving outputs...")

rows = []
for rule, m, lags_vars, coefs, ses, tstats, pvals, cilos, cihis, sigs, note in [
    ('A', model_A,
     ['flood_exposure_ruleA_qt', 'flood_ruleA_L1', 'flood_ruleA_L2'],
     [coef_A_t0, coef_A_t1, coef_A_t2],
     [se_A_t0,   se_A_t1,   se_A_t2  ],
     [t_A_t0,    t_A_t1,    t_A_t2   ],
     [p_A_t0,    p_A_t1,    p_A_t2   ],
     [cilo_A_t0, cilo_A_t1, cilo_A_t2],
     [cihi_A_t0, cihi_A_t1, cihi_A_t2],
     [sig_A_t0,  sig_A_t1,  sig_A_t2 ],
     'Primary. Quarter FE only. Validated Feb 6 (t-2 beta=-0.0091, p=0.012).'),
    ('B', model_B,
     ['flood_exposure_ruleB_qt', 'flood_ruleB_L1', 'flood_ruleB_L2'],
     [coef_B_t0, coef_B_t1, coef_B_t2],
     [se_B_t0,   se_B_t1,   se_B_t2  ],
     [t_B_t0,    t_B_t1,    t_B_t2   ],
     [p_B_t0,    p_B_t1,    p_B_t2   ],
     [cilo_B_t0, cilo_B_t1, cilo_B_t2],
     [cihi_B_t0, cihi_B_t1, cihi_B_t2],
     [sig_B_t0,  sig_B_t1,  sig_B_t2 ],
     'Robustness. District-only match. Lower power.')
]:
    lag_labels = ['t0', 't-1', 't-2']
    for i in range(3):
        rows.append({
            'hypothesis':        'H3',
            'rule':              rule,
            'lag':               lag_labels[i],
            'variable':          lags_vars[i],
            'coefficient':       round(coefs[i],  6),
            'std_error':         round(ses[i],    6),
            't_statistic':       round(tstats[i], 3),
            'p_value':           round(pvals[i],  6),
            'ci_lower_95':       round(cilos[i],  6),
            'ci_upper_95':       round(cihis[i],  6),
            'n_obs':             int(m.nobs),
            'r_squared':         round(m.rsquared, 4),
            'r_squared_adj':     round(m.rsquared_adj, 4),
            'quarter_fe_count':  n_qfe_A,
            'district_fe':       'NONE (pre-committed H3 specification)',
            'se_type':           'clustered_by_district_state_id',
            'significance':      sigs[i],
            'note':              note
        })

results_df = pd.DataFrame(rows)
results_df.to_csv('05_Outputs/Tables/04_H3_timing.csv', index=False)
print(f"  Table saved: 05_Outputs/Tables/04_H3_timing.csv")
log.info(f"\nTable saved: 05_Outputs/Tables/04_H3_timing.csv")

with open('05_Outputs/Logs/29_H3_regression_full_ruleA.txt', 'w') as f:
    f.write(str(model_A.summary()))
print(f"  Full summary (Rule A): 05_Outputs/Logs/29_H3_regression_full_ruleA.txt")
log.info("Full summary (Rule A) saved.")

with open('05_Outputs/Logs/29_H3_regression_full_ruleB.txt', 'w') as f:
    f.write(str(model_B.summary()))
print(f"  Full summary (Rule B): 05_Outputs/Logs/29_H3_regression_full_ruleB.txt")
log.info("Full summary (Rule B) saved.")


# === COMPLETION ===
print("\n" + "=" * 70)
print("H3 DISTRIBUTED LAG COMPLETE")
print("=" * 70)
print(f"  Table:         05_Outputs/Tables/04_H3_timing.csv")
print(f"  Log:           05_Outputs/Logs/29_H3_regression.txt")
print(f"  Full (Rule A): 05_Outputs/Logs/29_H3_regression_full_ruleA.txt")
print(f"  Full (Rule B): 05_Outputs/Logs/29_H3_regression_full_ruleB.txt")
print("=" * 70)
print("NEXT STEP: Run Script 30 (H4: Heterogeneity)")
print("=" * 70)

log.info("\n" + "=" * 70)
log.info("SCRIPT 29 COMPLETE")
log.info("Next: Script 30 -- H4 Heterogeneity")
log.info("=" * 70)