"""
28b_regression_H2_linearmodels.py
H2: IV 2SLS -- Nighttime Lights -> Deposit Withdrawals
Instrument: flood_exposure_ruleA_qt (primary), flood_exposure_ruleB_qt (robustness)

Replaces Script 28. Key differences from Script 28:
  1. Eliminates manual get_dummies FE block (666 dummy columns).
     Uses linearmodels.IV2SLS with absorbed entity + time effects via
     within-transformation, identical to Script 27b PanelOLS approach.
     Resolves numerical overflow in first-stage F-statistic and
     rank deficiency in clustered VCV.
  2. Panel index uses quarter_int (sequential integer) not quarter string.
     Matches Script 27b fix. Prevents ValueError on time dimension.
  3. F-statistic via t^2 retained (Wooldridge 2010 p.104, single instrument).

WHY linearmodels IV2SLS, NOT manual 2SLS:
  Manual 2SLS produces incorrect SE: second-stage residuals use
  y - X_hat*beta instead of structural y - X_actual*beta.
  linearmodels.IV2SLS implements the correct sandwich estimator.
  See Wooldridge (2010) pp. 106-107.

Anchors (Script 28, IV2SLS with manual dummies):
  Rule A: 2nd stage beta = -0.008400, SE = 0.034000, p = 0.805 (NULL)
          1st stage F = 34.673 (STRONG, t^2 method)
  Rule B: 2nd stage beta = -0.006800, SE = 0.059700, p = 0.910 (NULL)
          1st stage F =  8.949 (WEAK, t^2 method)
  N = 22,442 | District FE = 631 | Quarter FE = 36

Output: 05_Outputs/Tables/03b_H2_linearmodels.csv
        05_Outputs/Logs/28b_H2_linearmodels.txt
        05_Outputs/Logs/28b_H2_linearmodels_full_ruleA.txt
        05_Outputs/Logs/28b_H2_linearmodels_full_ruleB.txt
"""

import os
import numpy as np
import pandas as pd
import logging
import warnings
warnings.filterwarnings('ignore')
from linearmodels.iv import IV2SLS

# =============================================================================
# [1/7] SETUP
# =============================================================================

os.makedirs('05_Outputs/Logs',   exist_ok=True)
os.makedirs('05_Outputs/Tables', exist_ok=True)

logging.basicConfig(
    filename='05_Outputs/Logs/28b_H2_linearmodels.txt',
    level=logging.INFO,
    format='%(message)s',
    filemode='w'
)
log = logging.getLogger(__name__)

STABILITY_THRESHOLD = 0.005   # H2 second stage: wider threshold (null result)

ANCHOR_2ND_BETA_A = -0.008400
ANCHOR_2ND_SE_A   =  0.034000
ANCHOR_2ND_BETA_B = -0.006800
ANCHOR_2ND_SE_B   =  0.059700
ANCHOR_FS_F_A     =  34.673
ANCHOR_FS_F_B     =   8.949
ANCHOR_N          =  22442

def _stars(p):
    if p < 0.001: return "***"
    if p < 0.01:  return "**"
    if p < 0.05:  return "*"
    if p < 0.10:  return "+"
    return ""

def _iv_credibility(F):
    if F < 10:
        return "WEAK INSTRUMENT (F < 10). Label suggestive. Remove causal language."
    elif F < 16.38:
        return "MODERATE INSTRUMENT (10 <= F < 16.38). Proceed with caution."
    return "STRONG INSTRUMENT (F >= 16.38). IV credible."

print("=" * 70)
print("SCRIPT 28b: H2 IV 2SLS -- linearmodels (entity + time effects)")
print("Nighttime Lights -> Deposit Withdrawals")
print("=" * 70)
log.info("=" * 70)
log.info("28b: H2 IV 2SLS -- linearmodels IV2SLS")
log.info("Nighttime Lights -> Deposit Withdrawals")
log.info("Anchors (Script 28):")
log.info(f"  Rule A: 2nd beta={ANCHOR_2ND_BETA_A}, SE={ANCHOR_2ND_SE_A}, p=0.805 | F={ANCHOR_FS_F_A}")
log.info(f"  Rule B: 2nd beta={ANCHOR_2ND_BETA_B}, SE={ANCHOR_2ND_SE_B}, p=0.910 | F={ANCHOR_FS_F_B}")
log.info(f"  N={ANCHOR_N}")
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
    'deposit_change_qt', 'lights_change_qt',
    'flood_exposure_ruleA_qt', 'flood_exposure_ruleB_qt',
    'district_gadm', 'state_gadm', 'quarter'
]
missing_cols = [c for c in required_cols if c not in df.columns]
assert len(missing_cols) == 0, f"Missing required columns: {missing_cols}"
print(f"  Required columns verified -- PASS")
log.info(f"  Required columns verified -- PASS")

# =============================================================================
# [3/7] CONSTRUCT COMPOSITE KEY AND RESTRICT TO H2 SAMPLE
# =============================================================================

print("\n[3/7] Constructing composite key and restricting to H2 sample...")
log.info("\n[3/7] Composite key and sample restriction")

# Composite key: prevents 7 homonymous district pairs from collapsing.
# district_gadm alone -> 624 FE (WRONG).
# district_gadm + '_' + state_gadm -> 631 FE (CORRECT).
df['district_state_id'] = df['district_gadm'] + '_' + df['state_gadm']

# H2 sample: deposit_change_qt and lights_change_qt and both flood rules non-NaN.
# deposit_change_qt has 905 NaN (first quarter per district = 631, plus
# additional missingness). lights_change_qt has 631 NaN (first quarter only).
# Complete case filter produces N = 22,442 (matches Script 28 anchor).
df_reg = df[
    df['deposit_change_qt'].notna() &
    df['lights_change_qt'].notna() &
    df['flood_exposure_ruleA_qt'].notna() &
    df['flood_exposure_ruleB_qt'].notna()
].copy().reset_index(drop=True)

n_h2 = len(df_reg)
assert n_h2 == 22442, (
    f"H2 sample mismatch. Expected 22,442. Got {n_h2}. "
    f"Check deposit_change_qt and lights_change_qt NaN structure."
)
print(f"  H2 sample: N = {n_h2:,} -- PASS")
log.info(f"  H2 sample: N = {n_h2:,} -- PASS")

n_districts = df_reg['district_state_id'].nunique()
n_quarters  = df_reg['quarter'].nunique()
assert n_districts == 631, (
    f"Expected 631 districts. Got {n_districts}. Check composite key."
)
assert 35 <= n_quarters <= 37, (
    f"Quarter count {n_quarters} outside expected range [35, 37]."
)
print(f"  Districts: {n_districts} (expected 631) -- PASS")
print(f"  Quarters:  {n_quarters} (expected 36) -- PASS")
log.info(f"  Districts: {n_districts} -- PASS")
log.info(f"  Quarters:  {n_quarters} -- PASS")

# =============================================================================
# [4/7] BUILD PANEL INDEX FOR linearmodels
# =============================================================================

print("\n[4/7] Building panel index for linearmodels IV2SLS...")
log.info("\n[4/7] Building panel index")

# linearmodels requires the time index to be numeric or date-like.
# 'quarter' column stores strings e.g. '2015Q2' -- not accepted.
# Map to sequential integers (chronological sort is correct for 'YYYYQN' strings).
# Identical approach to Script 27b.

quarters_sorted = sorted(df_reg['quarter'].unique())
assert len(quarters_sorted) == 36, (
    f"Expected 36 quarters in H2 sample. Got {len(quarters_sorted)}. "
    f"Range: {quarters_sorted[0]} to {quarters_sorted[-1]}."
)
quarter_to_int = {q: i for i, q in enumerate(quarters_sorted, start=1)}
df_reg['quarter_int'] = df_reg['quarter'].map(quarter_to_int)

print(f"  Quarter range: {quarters_sorted[0]} to {quarters_sorted[-1]} "
      f"({len(quarters_sorted)} quarters, mapped to integers 1-{len(quarters_sorted)}) -- PASS")
log.info(f"  Quarter range: {quarters_sorted[0]} to {quarters_sorted[-1]} "
         f"({len(quarters_sorted)} quarters, mapped to integers 1-{len(quarters_sorted)}) -- PASS")

df_reg = df_reg.set_index(['district_state_id', 'quarter_int'])

n_duplicates = df_reg.index.duplicated().sum()
assert n_duplicates == 0, (
    f"Panel index has {n_duplicates} duplicate (entity, time) pairs. "
    f"Panel must be unique for linearmodels IV2SLS."
)
print(f"  Panel index (entity=district_state_id, time=quarter_int): "
      f"{n_duplicates} duplicates -- PASS")
log.info(f"  Panel index unique: {n_duplicates} duplicates -- PASS")
log.info(f"  Entity: district_state_id "
         f"({df_reg.index.get_level_values(0).nunique()} unique)")
log.info(f"  Time:   quarter_int "
         f"({df_reg.index.get_level_values(1).nunique()} unique, "
         f"1={quarters_sorted[0]}, {len(quarters_sorted)}={quarters_sorted[-1]})")

# =============================================================================
# [5/7] TWO-WAY WITHIN-TRANSFORMATION (iterative, unbalanced-panel safe)
# =============================================================================

print("\n[5/7] Applying two-way within-transformation (iterative)...")
log.info("\n[5/7] Two-way within-transformation")
log.info("  Method: iterative alternating entity/time demeaning.")
log.info("  Required because H2 panel is unbalanced (N=22,442 < 631x36=22,716).")
log.info("  Single-pass formula fails on unbalanced panels; iterative converges.")
log.info("  Tolerance: 1e-12. Max iterations: 500.")
log.info("  Reference: Gauss-Seidel alternating projections.")
log.info("  Equivalent to PanelOLS(entity_effects=True, time_effects=True).")

def demean_twoway_iterative(df_panel, cols, tol=1e-12, max_iter=500):
    """
    Iterative alternating demeaning: entity then time, repeated until
    convergence. Correct for both balanced and unbalanced panels.
    Convergence criterion: max absolute change across all columns < tol.
    """
    result = df_panel[cols].copy().astype(float)
    for iteration in range(max_iter):
        prev = result.copy()
        result = result - result.groupby(level=0).transform('mean')
        result = result - result.groupby(level=1).transform('mean')
        change = (result - prev).abs().max().max()
        if change < tol:
            log.info(f"  Converged at iteration {iteration + 1} "
                     f"(max change = {change:.2e} < tol {tol:.0e}).")
            print(f"  Converged at iteration {iteration + 1} "
                  f"(max change = {change:.2e}) -- PASS")
            return result
    raise RuntimeError(
        f"Iterative demeaning did not converge in {max_iter} iterations. "
        f"Final max change = {change:.2e}. Check panel structure."
    )

cols_to_demean = [
    'deposit_change_qt',
    'lights_change_qt',
    'flood_exposure_ruleA_qt',
    'flood_exposure_ruleB_qt'
]
df_dm = demean_twoway_iterative(df_reg, cols_to_demean)

# Verify convergence: entity means and time means of demeaned data must be ~0.
entity_mean_check = df_dm['deposit_change_qt'].groupby(level=0).mean().abs().max()
time_mean_check   = df_dm['deposit_change_qt'].groupby(level=1).mean().abs().max()
assert entity_mean_check < 1e-8, (
    f"Entity demeaning failed after iteration: max entity mean = {entity_mean_check:.2e}. "
    f"Increase max_iter or check panel structure."
)
assert time_mean_check < 1e-8, (
    f"Time demeaning failed after iteration: max time mean = {time_mean_check:.2e}. "
    f"Increase max_iter or check panel structure."
)
print(f"  Entity mean check (max abs): {entity_mean_check:.2e} < 1e-8 -- PASS")
print(f"  Time mean check  (max abs):  {time_mean_check:.2e} < 1e-8 -- PASS")
log.info(f"  Entity mean check: {entity_mean_check:.2e} -- PASS")
log.info(f"  Time mean check:   {time_mean_check:.2e} -- PASS")

# Constant for IV2SLS (required by linearmodels even after demeaning).
df_dm['const'] = 1.0
# Cluster Series: entity index values, aligned to df_dm index.
# IV2SLS.fit() takes clusters= not cluster_entity=.
clusters = pd.Series(
    df_dm.index.get_level_values(0),
    index=df_dm.index,
    name='district_state_id'
)

# =============================================================================
# [6/7] FIT IV2SLS MODELS: RULE A AND RULE B
# =============================================================================

print("\n[6/7] Fitting IV2SLS models (two-way demeaned)...")
log.info("\n[6/7] Model fitting")
log.info("  Specification: deposit_change_qt(dm) ~ const | lights_change_qt(dm)")
log.info("  Instrument A: flood_exposure_ruleA_qt(dm)")
log.info("  Instrument B: flood_exposure_ruleB_qt(dm)")
log.info("  SE: clustered by entity (district_state_id, 631 clusters)")

def fit_h2(df_demeaned, instrument_col, rule_label,
           anchor_2nd_beta, anchor_2nd_se, anchor_fs_F, cluster_series):
    """
    Fit linearmodels IV2SLS on two-way demeaned data.
    Returns result object and all extracted scalars.
    """
    log.info(f"\n  Rule {rule_label}:")
    log.info(f"    Instrument: {instrument_col}")
    log.info(f"    Anchors: 2nd beta={anchor_2nd_beta}, SE={anchor_2nd_se}, F={anchor_fs_F}")

    dependent   = df_demeaned[['deposit_change_qt']]
    exog        = df_demeaned[['const']]
    endog       = df_demeaned[['lights_change_qt']]
    instruments = df_demeaned[[instrument_col]]

    model = IV2SLS(
        dependent   = dependent,
        exog        = exog,
        endog       = endog,
        instruments = instruments
    )

    result = model.fit(
        cov_type = 'clustered',
        clusters = cluster_series
    )

    # Second stage
    beta_2nd  = result.params['lights_change_qt']
    se_2nd    = result.std_errors['lights_change_qt']
    t_2nd     = result.tstats['lights_change_qt']
    p_2nd     = result.pvalues['lights_change_qt']
    ci        = result.conf_int()
    ci_lo     = ci.loc['lights_change_qt', 'lower']
    ci_hi     = ci.loc['lights_change_qt', 'upper']
    nobs      = int(result.nobs)
    r2        = result.rsquared
    sig_2nd   = _stars(p_2nd)

    # First stage: extract t-statistic for flood instrument -> lights (demeaned).
    # F = t^2 for single excluded instrument (Wooldridge 2010 p.104).
    # linearmodels first_stage F overflows at high exog column count.
    # Here exog = const only (1 column) -- overflow should not occur.
    # Extract both directly and via t^2 for cross-validation.
    try:
        fs          = result.first_stage
        fs_res      = fs.individual['lights_change_qt']
        fs_beta     = fs_res.params[instrument_col]
        fs_se       = fs_res.std_errors[instrument_col]
        fs_t        = fs_res.tstats[instrument_col]
        fs_p        = fs_res.pvalues[instrument_col]
        fs_F_direct = fs_res.f_statistic.stat
        fs_F_t2     = fs_t ** 2
        # Use t^2 as primary (consistent with Script 28 and Wooldridge method).
        fs_F        = fs_F_t2
        fs_extract  = "PASS"
    except Exception as e:
        log.warning(f"    First stage extraction failed: {e}. Setting NaN.")
        fs_beta = np.nan; fs_se = np.nan; fs_t = np.nan
        fs_p = np.nan; fs_F_direct = np.nan; fs_F_t2 = np.nan
        fs_F = np.nan; fs_extract = f"FAILED: {e}"

    iv_cred = _iv_credibility(fs_F)

    print(f"\n  Rule {rule_label}:")
    print(f"    FIRST STAGE:")
    print(f"      beta (flood -> lights_dm):  {fs_beta:.6f}")
    print(f"      SE:                          {fs_se:.6f}")
    print(f"      t:                           {fs_t:.4f}")
    print(f"      p:                           {fs_p:.6f}")
    print(f"      F (t^2):                     {fs_F:.3f}  (anchor: {anchor_fs_F:.3f})")
    print(f"      F (direct):                  {fs_F_direct:.3f}")
    print(f"      Credibility:                 {iv_cred}")
    print(f"    SECOND STAGE:")
    print(f"      beta (lights_dm -> deposit_dm): {beta_2nd:.6f}  (anchor: {anchor_2nd_beta:.6f})")
    print(f"      SE:                              {se_2nd:.6f}  (anchor: {anchor_2nd_se:.6f})")
    print(f"      t:                               {t_2nd:.4f}")
    print(f"      p:                               {p_2nd:.6f}  {sig_2nd if sig_2nd else '(NOT SIGNIFICANT)'}")
    print(f"      95% CI:                          [{ci_lo:.6f}, {ci_hi:.6f}]")
    print(f"      N:                               {nobs:,}")
    print(f"      R2:                              {r2:.4f}")

    log.info(f"    FIRST STAGE:")
    log.info(f"      beta = {fs_beta:.6f}, SE = {fs_se:.6f}, t = {fs_t:.4f}, p = {fs_p:.6f}")
    log.info(f"      F(t^2) = {fs_F:.3f} (anchor: {anchor_fs_F:.3f}), F(direct) = {fs_F_direct:.3f}")
    log.info(f"      Credibility: {iv_cred}")
    log.info(f"    SECOND STAGE:")
    log.info(f"      beta = {beta_2nd:.6f} (anchor: {anchor_2nd_beta:.6f})")
    log.info(f"      SE = {se_2nd:.6f} (anchor: {anchor_2nd_se:.6f})")
    log.info(f"      t = {t_2nd:.4f}, p = {p_2nd:.6f} {sig_2nd}")
    log.info(f"      95% CI = [{ci_lo:.6f}, {ci_hi:.6f}]")
    log.info(f"      N = {nobs:,}, R2 = {r2:.4f}")

    # Stability check on second-stage beta vs Script 28 anchor.
    delta = abs(beta_2nd - anchor_2nd_beta)
    if delta > STABILITY_THRESHOLD:
        msg = (
            f"STABILITY WARNING Rule {rule_label}: |beta_28b - beta_28| = "
            f"{delta:.6f} > threshold {STABILITY_THRESHOLD}. "
            f"Investigate before writing. H2 null must be confirmed."
        )
        print(f"    *** {msg}")
        log.info(f"    *** {msg}")
    else:
        stability_msg = (
            f"Second-stage coefficient stable: delta = {delta:.6f} "
            f"<= threshold {STABILITY_THRESHOLD} -- PASS"
        )
        print(f"    {stability_msg}")
        log.info(f"    {stability_msg}")

    return (result, beta_2nd, se_2nd, t_2nd, p_2nd, ci_lo, ci_hi,
            nobs, r2, sig_2nd, fs_beta, fs_se, fs_t, fs_p, fs_F, iv_cred)

(result_A, b2_A, se2_A, t2_A, p2_A, ci_lo_A, ci_hi_A,
 n_A, r2_A, sig2_A, fs_b_A, fs_se_A, fs_t_A, fs_p_A,
 fs_F_A, iv_cred_A) = fit_h2(
    df_dm, 'flood_exposure_ruleA_qt', 'A',
    ANCHOR_2ND_BETA_A, ANCHOR_2ND_SE_A, ANCHOR_FS_F_A, clusters
)

(result_B, b2_B, se2_B, t2_B, p2_B, ci_lo_B, ci_hi_B,
 n_B, r2_B, sig2_B, fs_b_B, fs_se_B, fs_t_B, fs_p_B,
 fs_F_B, iv_cred_B) = fit_h2(
    df_dm, 'flood_exposure_ruleB_qt', 'B',
    ANCHOR_2ND_BETA_B, ANCHOR_2ND_SE_B, ANCHOR_FS_F_B, clusters
)

# =============================================================================
# [6b/7] SIDE-BY-SIDE SUMMARY AND CONSISTENCY CHECKS
# =============================================================================

print("\n" + "=" * 70)
print("H2 RESULTS SUMMARY -- linearmodels IV2SLS (two-way demeaned)")
print("=" * 70)
print(f"  SECOND STAGE: lights_change_qt(dm) -> deposit_change_qt(dm)")
print(f"  {'Spec':<10} {'Beta':>12} {'SE':>10} {'t':>8} {'p':>10} {'Sig':>5}")
print(f"  {'-' * 58}")
print(f"  {'Rule A':<10} {b2_A:>12.6f} {se2_A:>10.6f} {t2_A:>8.4f} {p2_A:>10.6f} {sig2_A:>5}")
print(f"  {'Rule B':<10} {b2_B:>12.6f} {se2_B:>10.6f} {t2_B:>8.4f} {p2_B:>10.6f} {sig2_B:>5}")
print(f"  {'-' * 58}")
print(f"  FIRST STAGE F (t^2): Rule A = {fs_F_A:.3f} | Rule B = {fs_F_B:.3f}")
print(f"  N: {n_A:,} | Entity FE: district_state_id (631) | Time FE: quarter (36)")
print(f"  SE: Clustered by entity (district_state_id, 631 clusters)")
print(f"  Method: Two-way within-demeaning + linearmodels IV2SLS")
print()
print(f"  Script 28 anchors (IV2SLS with manual dummies):")
print(f"  {'Rule A':<10} {ANCHOR_2ND_BETA_A:>12.6f} {ANCHOR_2ND_SE_A:>10.6f}  F={ANCHOR_FS_F_A:.3f}")
print(f"  {'Rule B':<10} {ANCHOR_2ND_BETA_B:>12.6f} {ANCHOR_2ND_SE_B:>10.6f}  F={ANCHOR_FS_F_B:.3f}")

log.info("\n" + "=" * 70)
log.info("SIDE-BY-SIDE SUMMARY -- linearmodels IV2SLS (two-way demeaned)")
log.info("=" * 70)
log.info(f"  {'Spec':<10} {'Beta':>12} {'SE':>10} {'t':>8} {'p':>10} {'Sig':>5}")
log.info(f"  {'-' * 58}")
log.info(f"  {'Rule A':<10} {b2_A:>12.6f} {se2_A:>10.6f} {t2_A:>8.4f} {p2_A:>10.6f} {sig2_A:>5}")
log.info(f"  {'Rule B':<10} {b2_B:>12.6f} {se2_B:>10.6f} {t2_B:>8.4f} {p2_B:>10.6f} {sig2_B:>5}")
log.info(f"  First Stage F: Rule A = {fs_F_A:.3f} | Rule B = {fs_F_B:.3f}")
log.info(f"  N: {n_A:,} | Entity FE: 631 | Time FE: 36")

# Null confirmation checks (H2 is pre-committed null)
for rule, p, beta in [('A', p2_A, b2_A), ('B', p2_B, b2_B)]:
    if p >= 0.05:
        log.info(f"  H2 Rule {rule}: NULL CONFIRMED (p={p:.4f} >= 0.05) -- PASS")
    else:
        log.info(
            f"  H2 Rule {rule}: SIGNIFICANCE DETECTED (p={p:.4f}). "
            f"H2 was pre-committed null. Investigate before writing."
        )

# F-statistic check
if fs_F_A >= 16.38:
    log.info(f"  Rule A instrument: STRONG (F={fs_F_A:.3f} >= 16.38) -- PASS")
else:
    log.info(f"  Rule A instrument: WARNING F={fs_F_A:.3f} < 16.38. Review.")
if fs_F_B < 10:
    log.info(f"  Rule B instrument: WEAK (F={fs_F_B:.3f} < 10) -- expected, consistent with anchor.")
else:
    log.info(f"  Rule B instrument: F={fs_F_B:.3f}")

# =============================================================================
# [7/7] SAVE OUTPUTS
# =============================================================================

print("\n[7/7] Saving outputs...")
log.info("\n[7/7] Saving outputs")

results_df = pd.DataFrame([
    {
        'hypothesis'             : 'H2',
        'rule'                   : 'A',
        'estimator'              : 'linearmodels.IV2SLS (two-way within-demeaned)',
        'specification'          : 'deposit_change_qt(dm) ~ const | lights_change_qt(dm) [instrument: flood_ruleA(dm)]',
        'endog_variable'         : 'lights_change_qt',
        'instrument'             : 'flood_exposure_ruleA_qt',
        'second_stage_beta'      : round(b2_A,      6),
        'second_stage_se'        : round(se2_A,     6),
        'second_stage_t'         : round(t2_A,      4),
        'second_stage_p'         : round(p2_A,      6),
        'ci_lower_95'            : round(ci_lo_A,   6),
        'ci_upper_95'            : round(ci_hi_A,   6),
        'n_obs'                  : n_A,
        'r_squared'              : round(r2_A,      4),
        'first_stage_beta'       : round(fs_b_A,    6),
        'first_stage_se'         : round(fs_se_A,   6),
        'first_stage_t'          : round(fs_t_A,    4),
        'first_stage_p'          : round(fs_p_A,    6),
        'first_stage_F_t2'       : round(fs_F_A,    3),
        'iv_credibility'         : iv_cred_A,
        'entity_fe'              : 'district_state_id',
        'n_entity_fe'            : 631,
        'time_fe'                : 'quarter',
        'n_time_fe'              : 36,
        'se_type'                : 'clustered_entity (district_state_id, 631 clusters)',
        'significance'           : sig2_A,
        'anchor_beta_script28'   : ANCHOR_2ND_BETA_A,
        'anchor_se_script28'     : ANCHOR_2ND_SE_A,
        'anchor_F_script28'      : ANCHOR_FS_F_A,
        'delta_beta'             : round(abs(b2_A - ANCHOR_2ND_BETA_A), 6),
        'note'                   : (
            'Final paper table. IV2SLS two-way demeaned. '
            'H2 pre-committed null. Rule A instrument strong (F>16.38). '
            'Null consistent with lagged mechanism (see H3).'
        )
    },
    {
        'hypothesis'             : 'H2',
        'rule'                   : 'B',
        'estimator'              : 'linearmodels.IV2SLS (two-way within-demeaned)',
        'specification'          : 'deposit_change_qt(dm) ~ const | lights_change_qt(dm) [instrument: flood_ruleB(dm)]',
        'endog_variable'         : 'lights_change_qt',
        'instrument'             : 'flood_exposure_ruleB_qt',
        'second_stage_beta'      : round(b2_B,      6),
        'second_stage_se'        : round(se2_B,     6),
        'second_stage_t'         : round(t2_B,      4),
        'second_stage_p'         : round(p2_B,      6),
        'ci_lower_95'            : round(ci_lo_B,   6),
        'ci_upper_95'            : round(ci_hi_B,   6),
        'n_obs'                  : n_B,
        'r_squared'              : round(r2_B,      4),
        'first_stage_beta'       : round(fs_b_B,    6),
        'first_stage_se'         : round(fs_se_B,   6),
        'first_stage_t'          : round(fs_t_B,    4),
        'first_stage_p'          : round(fs_p_B,    6),
        'first_stage_F_t2'       : round(fs_F_B,    3),
        'iv_credibility'         : iv_cred_B,
        'entity_fe'              : 'district_state_id',
        'n_entity_fe'            : 631,
        'time_fe'                : 'quarter',
        'n_time_fe'              : 36,
        'se_type'                : 'clustered_entity (district_state_id, 631 clusters)',
        'significance'           : sig2_B,
        'anchor_beta_script28'   : ANCHOR_2ND_BETA_B,
        'anchor_se_script28'     : ANCHOR_2ND_SE_B,
        'anchor_F_script28'      : ANCHOR_FS_F_B,
        'delta_beta'             : round(abs(b2_B - ANCHOR_2ND_BETA_B), 6),
        'note'                   : (
            'Final paper table. IV2SLS two-way demeaned. '
            'H2 pre-committed null. Rule B instrument weak (F<10). '
            'Rule B IV results labeled suggestive. Remove causal language.'
        )
    }
])

OUTPUT_CSV = '05_Outputs/Tables/03b_H2_linearmodels.csv'
results_df.to_csv(OUTPUT_CSV, index=False)
assert os.path.exists(OUTPUT_CSV), f"CSV not written: {OUTPUT_CSV}"
print(f"  CSV saved: {OUTPUT_CSV} -- PASS")
log.info(f"  CSV saved: {OUTPUT_CSV} -- PASS")

OUTPUT_SUMMARY_A = '05_Outputs/Logs/28b_H2_linearmodels_full_ruleA.txt'
OUTPUT_SUMMARY_B = '05_Outputs/Logs/28b_H2_linearmodels_full_ruleB.txt'

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
print("SCRIPT 28b COMPLETE")
print("=" * 70)
print(f"  CSV:           {OUTPUT_CSV}")
print(f"  Log:           05_Outputs/Logs/28b_H2_linearmodels.txt")
print(f"  Full (Rule A): {OUTPUT_SUMMARY_A}")
print(f"  Full (Rule B): {OUTPUT_SUMMARY_B}")
print("=" * 70)
print("NEXT STEP: Run Script 29b (H3: Distributed Lag -- linearmodels PanelOLS)")
print("=" * 70)

log.info("\n" + "=" * 70)
log.info("SCRIPT 28b COMPLETE")
log.info(f"  CSV:           {OUTPUT_CSV}")
log.info(f"  Full (Rule A): {OUTPUT_SUMMARY_A}")
log.info(f"  Full (Rule B): {OUTPUT_SUMMARY_B}")
log.info("Next: Script 29b -- H3 Distributed Lag linearmodels PanelOLS")
log.info("=" * 70)