"""
27b_regression_H1_linearmodels.py
H1: Floods -> Nighttime Lights Decline
linearmodels PanelOLS with entity (district) + time (quarter) effects.
Replaces statsmodels OLS from Script 27. Resolves ValueWarning from
rank deficiency in clustered VCV at 666 exogenous columns.
Final paper table version.

Anchors (Script 27, statsmodels):
  Rule A: beta = -0.044500, SE = 0.007800, t = -5.708, p < 0.001
  Rule B: beta = -0.058400, SE = 0.019800, t = -2.954, p = 0.003

Output: 05_Outputs/Tables/02b_H1_linearmodels.csv
        05_Outputs/Logs/27b_H1_linearmodels.txt
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
    filename='05_Outputs/Logs/27b_H1_linearmodels.txt',
    level=logging.INFO,
    format='%(message)s',
    filemode='w'
)
log = logging.getLogger(__name__)

# Coefficient stability threshold: flag if linearmodels beta differs
# from Script 27 statsmodels beta by more than this amount.
STABILITY_THRESHOLD = 0.001

ANCHOR_BETA_A = -0.044500
ANCHOR_SE_A   =  0.007800
ANCHOR_BETA_B = -0.058400
ANCHOR_SE_B   =  0.019800

def _stars(p):
    if p < 0.001: return "***"
    if p < 0.01:  return "**"
    if p < 0.05:  return "*"
    if p < 0.10:  return "+"
    return ""

print("=" * 70)
print("SCRIPT 27b: H1 FIRST STAGE -- linearmodels PanelOLS")
print("Floods -> Nighttime Lights Decline")
print("=" * 70)
log.info("=" * 70)
log.info("27b: H1 FIRST STAGE -- linearmodels PanelOLS")
log.info("Floods -> Nighttime Lights Decline")
log.info("Anchors (Script 27 statsmodels):")
log.info(f"  Rule A: beta = {ANCHOR_BETA_A}, SE = {ANCHOR_SE_A}, p < 0.001")
log.info(f"  Rule B: beta = {ANCHOR_BETA_B}, SE = {ANCHOR_SE_B}, p = 0.003")
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
    'lights_change_qt', 'deposit_change_qt',
    'flood_exposure_ruleA_qt', 'flood_exposure_ruleB_qt',
    'district_gadm', 'state_gadm', 'quarter'
]
missing_cols = [c for c in required_cols if c not in df.columns]
assert len(missing_cols) == 0, f"Missing required columns: {missing_cols}"
print(f"  Required columns verified -- PASS")
log.info(f"  Required columns verified -- PASS")

# =============================================================================
# [3/7] CONSTRUCT COMPOSITE KEY AND RESTRICT TO H1 SAMPLE
# =============================================================================

print("\n[3/7] Constructing composite key and restricting to H1 sample...")
log.info("\n[3/7] Composite key and sample restriction")

# Composite key: prevents 7 homonymous district pairs from collapsing.
# district_gadm alone -> 624 FE (WRONG).
# district_gadm + '_' + state_gadm -> 631 FE (CORRECT).
# Identical construction to Scripts 27, 36, 36b.
df['district_state_id'] = df['district_gadm'] + '_' + df['state_gadm']

# H1 sample: drop rows where lights_change_qt is NaN.
# Exactly 631 NaN -- one per district (first quarter has no prior period).
# Both flood rules have zero additional NaN, so one filter covers both.
df_reg = df[
    df['lights_change_qt'].notna() &
    df['flood_exposure_ruleA_qt'].notna() &
    df['flood_exposure_ruleB_qt'].notna()
].copy().reset_index(drop=True)

n_h1 = len(df_reg)
assert n_h1 == 22716, (
    f"H1 sample mismatch. Expected 22,716. Got {n_h1}. "
    f"23,347 - 631 first-quarter NaN = 22,716."
)
print(f"  H1 sample: N = {n_h1:,} -- PASS")
log.info(f"  H1 sample: N = {n_h1:,} -- PASS")

n_districts = df_reg['district_state_id'].nunique()
n_quarters  = df_reg['quarter'].nunique()
assert n_districts == 631, (
    f"Expected 631 districts. Got {n_districts}. Check composite key."
)
assert 35 <= n_quarters <= 37, (
    f"Quarter count {n_quarters} outside expected range [35, 37]."
)
print(f"  Districts: {n_districts} (expected 631) -- PASS")
print(f"  Quarters:  {n_quarters} (expected 36 in H1 sample) -- PASS")
log.info(f"  Districts: {n_districts} -- PASS")
log.info(f"  Quarters:  {n_quarters} -- PASS")

# =============================================================================
# [4/7] BUILD PANEL INDEX FOR linearmodels
# =============================================================================

print("\n[4/7] Building panel index for linearmodels PanelOLS...")
log.info("\n[4/7] Building panel index")

# linearmodels requires the time index to be numeric or date-like.
# The 'quarter' column stores strings e.g. '2015Q2' -- not accepted.
# pd.Period is unreliable across linearmodels versions.
# Safest: map quarter strings to sequential integers (1 = earliest quarter).
# Ordering is preserved because quarter strings are chronologically sortable.

df_reg = df_reg.reset_index(drop=True)

quarters_sorted = sorted(df_reg['quarter'].unique())
assert len(quarters_sorted) == 36, (
    f"Expected 36 quarters in H1 sample. Got {len(quarters_sorted)}. "
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
    f"Panel must be unique for linearmodels PanelOLS."
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
# [5/7] FIT MODELS: RULE A AND RULE B
# =============================================================================

print("\n[5/7] Fitting linearmodels PanelOLS models...")
log.info("\n[5/7] Model fitting")
log.info("  Specification: entity_effects=True, time_effects=True")
log.info("  SE:            cov_type='clustered', cluster_entity=True")
log.info("  Clusters:      district_state_id (631) -- entity index")
log.info("  Note:          cluster_entity=True clusters by the entity")
log.info("                 index (district_state_id), identical to")
log.info("                 Script 27 cov_kwds={'groups': district_state_id}.")

def fit_h1(df_panel, treatment_col, rule_label, anchor_beta, anchor_se):
    """
    Fit linearmodels PanelOLS for H1.
    Returns result object and extracted scalar statistics.
    """
    log.info(f"\n  Rule {rule_label}:")
    log.info(f"    Treatment: {treatment_col}")
    log.info(f"    Anchor beta = {anchor_beta}, SE = {anchor_se}")

    exog = df_panel[[treatment_col]]

    model = PanelOLS(
        dependent    = df_panel['lights_change_qt'],
        exog         = exog,
        entity_effects = True,
        time_effects   = True
    )

    result = model.fit(
        cov_type       = 'clustered',
        cluster_entity = True
    )

    beta   = result.params[treatment_col]
    se     = result.std_errors[treatment_col]
    tstat  = result.tstats[treatment_col]
    pval   = result.pvalues[treatment_col]
    ci     = result.conf_int()
    ci_lo  = ci.loc[treatment_col, 'lower']
    ci_hi  = ci.loc[treatment_col, 'upper']
    nobs   = int(result.nobs)
    r2_w   = result.rsquared           # within R-squared

    sig    = _stars(pval)

    print(f"\n  Rule {rule_label}:")
    print(f"    beta    = {beta:.6f}  (anchor: {anchor_beta:.6f})")
    print(f"    SE      = {se:.6f}  (anchor: {anchor_se:.6f})")
    print(f"    t       = {tstat:.4f}")
    print(f"    p       = {pval:.6f}  {sig}")
    print(f"    95% CI  = [{ci_lo:.6f}, {ci_hi:.6f}]")
    print(f"    N       = {nobs:,}")
    print(f"    R2(w)   = {r2_w:.4f}")

    log.info(f"    beta        = {beta:.6f}  (anchor: {anchor_beta:.6f})")
    log.info(f"    SE          = {se:.6f}  (anchor: {anchor_se:.6f})")
    log.info(f"    t           = {tstat:.4f}")
    log.info(f"    p           = {pval:.6f}  {sig}")
    log.info(f"    95% CI      = [{ci_lo:.6f}, {ci_hi:.6f}]")
    log.info(f"    N           = {nobs:,}")
    log.info(f"    R2 (within) = {r2_w:.4f}")

    # Coefficient stability check against Script 27 anchor.
    delta = abs(beta - anchor_beta)
    if delta > STABILITY_THRESHOLD:
        msg = (
            f"STABILITY WARNING Rule {rule_label}: |beta_linearmodels - "
            f"beta_script27| = {delta:.6f} > threshold {STABILITY_THRESHOLD}. "
            f"Investigate before writing. Do not proceed to paper tables."
        )
        print(f"    *** {msg}")
        log.info(f"    *** {msg}")
    else:
        stability_msg = (
            f"Coefficient stable: delta = {delta:.6f} "
            f"<= threshold {STABILITY_THRESHOLD} -- PASS"
        )
        print(f"    {stability_msg}")
        log.info(f"    {stability_msg}")

    return result, beta, se, tstat, pval, ci_lo, ci_hi, nobs, r2_w, sig

result_A, beta_A, se_A, t_A, p_A, ci_lo_A, ci_hi_A, n_A, r2_A, sig_A = fit_h1(
    df_reg, 'flood_exposure_ruleA_qt', 'A', ANCHOR_BETA_A, ANCHOR_SE_A
)

result_B, beta_B, se_B, t_B, p_B, ci_lo_B, ci_hi_B, n_B, r2_B, sig_B = fit_h1(
    df_reg, 'flood_exposure_ruleB_qt', 'B', ANCHOR_BETA_B, ANCHOR_SE_B
)

# =============================================================================
# [6/7] SIDE-BY-SIDE SUMMARY AND CONSISTENCY CHECKS
# =============================================================================

print("\n" + "=" * 70)
print("H1 RESULTS SUMMARY -- linearmodels PanelOLS")
print("=" * 70)
print(f"  {'Spec':<10} {'Beta':>12} {'SE':>10} {'t':>8} {'p':>10} {'Sig':>5}")
print(f"  {'-' * 58}")
print(f"  {'Rule A':<10} {beta_A:>12.6f} {se_A:>10.6f} {t_A:>8.4f} {p_A:>10.6f} {sig_A:>5}")
print(f"  {'Rule B':<10} {beta_B:>12.6f} {se_B:>10.6f} {t_B:>8.4f} {p_B:>10.6f} {sig_B:>5}")
print(f"  {'-' * 58}")
print(f"  N: {n_A:,} | Entity FE: district_state_id (631) | Time FE: quarter")
print(f"  SE: Clustered by entity (district_state_id, 631 clusters)")
print(f"  Method: linearmodels PanelOLS, entity_effects=True, time_effects=True")
print("")
print(f"  Script 27 anchors (statsmodels):")
print(f"  {'Rule A':<10} {ANCHOR_BETA_A:>12.6f} {ANCHOR_SE_A:>10.6f}")
print(f"  {'Rule B':<10} {ANCHOR_BETA_B:>12.6f} {ANCHOR_SE_B:>10.6f}")

log.info("\n" + "=" * 70)
log.info("SIDE-BY-SIDE SUMMARY -- linearmodels PanelOLS")
log.info("=" * 70)
log.info(f"  {'Spec':<10} {'Beta':>12} {'SE':>10} {'t':>8} {'p':>10} {'Sig':>5}")
log.info(f"  {'-' * 58}")
log.info(f"  {'Rule A':<10} {beta_A:>12.6f} {se_A:>10.6f} {t_A:>8.4f} {p_A:>10.6f} {sig_A:>5}")
log.info(f"  {'Rule B':<10} {beta_B:>12.6f} {se_B:>10.6f} {t_B:>8.4f} {p_B:>10.6f} {sig_B:>5}")
log.info(f"  N: {n_A:,} | Entity FE: 631 | Time FE: {df_reg.index.get_level_values(1).nunique()}")
log.info(f"  SE: clustered by entity (district_state_id)")

# Sign check: H1 predicts negative coefficient (floods reduce lights).
for rule, beta, pval in [('A', beta_A, p_A), ('B', beta_B, p_B)]:
    if beta > 0:
        log.info(
            f"  SIGN WARNING Rule {rule}: beta = {beta:.6f} is positive. "
            f"H1 predicts negative. Investigate before writing."
        )
    else:
        log.info(f"  Sign check Rule {rule}: negative (expected) -- PASS")

# =============================================================================
# [7/7] SAVE OUTPUTS
# =============================================================================

print("\n[7/7] Saving outputs...")
log.info("\n[7/7] Saving outputs")

results_df = pd.DataFrame([
    {
        'hypothesis'          : 'H1',
        'rule'                : 'A',
        'estimator'           : 'linearmodels.PanelOLS',
        'specification'       : 'lights_change_qt ~ flood_ruleA + EntityFE + TimeFE',
        'variable'            : 'flood_exposure_ruleA_qt',
        'coefficient'         : round(beta_A,   6),
        'std_error'           : round(se_A,     6),
        't_statistic'         : round(t_A,      4),
        'p_value'             : round(p_A,      6),
        'ci_lower_95'         : round(ci_lo_A,  6),
        'ci_upper_95'         : round(ci_hi_A,  6),
        'n_obs'               : n_A,
        'r_squared_within'    : round(r2_A,     4),
        'entity_fe'           : 'district_state_id',
        'n_entity_fe'         : 631,
        'time_fe'             : 'quarter',
        'se_type'             : 'clustered_entity (district_state_id, 631 clusters)',
        'significance'        : sig_A,
        'anchor_beta_script27': ANCHOR_BETA_A,
        'anchor_se_script27'  : ANCHOR_SE_A,
        'delta_beta'          : round(abs(beta_A - ANCHOR_BETA_A), 6),
        'note'                : (
            'Final paper table. linearmodels PanelOLS. '
            'Primary specification. State fallback in Rule A attenuates '
            'beta toward zero. Conservative lower bound.'
        )
    },
    {
        'hypothesis'          : 'H1',
        'rule'                : 'B',
        'estimator'           : 'linearmodels.PanelOLS',
        'specification'       : 'lights_change_qt ~ flood_ruleB + EntityFE + TimeFE',
        'variable'            : 'flood_exposure_ruleB_qt',
        'coefficient'         : round(beta_B,   6),
        'std_error'           : round(se_B,     6),
        't_statistic'         : round(t_B,      4),
        'p_value'             : round(p_B,      6),
        'ci_lower_95'         : round(ci_lo_B,  6),
        'ci_upper_95'         : round(ci_hi_B,  6),
        'n_obs'               : n_B,
        'r_squared_within'    : round(r2_B,     4),
        'entity_fe'           : 'district_state_id',
        'n_entity_fe'         : 631,
        'time_fe'             : 'quarter',
        'se_type'             : 'clustered_entity (district_state_id, 631 clusters)',
        'significance'        : sig_B,
        'anchor_beta_script27': ANCHOR_BETA_B,
        'anchor_se_script27'  : ANCHOR_SE_B,
        'delta_beta'          : round(abs(beta_B - ANCHOR_BETA_B), 6),
        'note'                : (
            'Final paper table. linearmodels PanelOLS. '
            'Robustness specification. District-only match. '
            'No state attenuation. Lower power (0.90% treatment rate).'
        )
    }
])

OUTPUT_CSV = '05_Outputs/Tables/02b_H1_linearmodels.csv'
results_df.to_csv(OUTPUT_CSV, index=False)
assert os.path.exists(OUTPUT_CSV), f"CSV not written: {OUTPUT_CSV}"
print(f"  CSV saved: {OUTPUT_CSV} -- PASS")
log.info(f"  CSV saved: {OUTPUT_CSV} -- PASS")

# Full linearmodels summary to text files.
OUTPUT_SUMMARY_A = '05_Outputs/Logs/27b_H1_linearmodels_full_ruleA.txt'
OUTPUT_SUMMARY_B = '05_Outputs/Logs/27b_H1_linearmodels_full_ruleB.txt'

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
print("SCRIPT 27b COMPLETE")
print("=" * 70)
print(f"  CSV:           {OUTPUT_CSV}")
print(f"  Log:           05_Outputs/Logs/27b_H1_linearmodels.txt")
print(f"  Full (Rule A): {OUTPUT_SUMMARY_A}")
print(f"  Full (Rule B): {OUTPUT_SUMMARY_B}")
print("=" * 70)
print("NEXT STEP: Run Script 28b (H2: IV 2SLS -- linearmodels IVLIML)")
print("=" * 70)

log.info("\n" + "=" * 70)
log.info("SCRIPT 27b COMPLETE")
log.info(f"  CSV:           {OUTPUT_CSV}")
log.info(f"  Full (Rule A): {OUTPUT_SUMMARY_A}")
log.info(f"  Full (Rule B): {OUTPUT_SUMMARY_B}")
log.info("Next: Script 28b -- H2 IV 2SLS linearmodels")
log.info("=" * 70)