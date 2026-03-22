"""
28_regression_H2_iv2sls.py
H2: IV 2SLS -- Nighttime Lights -> Deposit Withdrawals
Instrument: flood_exposure_ruleA_qt (primary), flood_exposure_ruleB_qt (robustness)
Estimator: linearmodels.IV2SLS with district + quarter FE, clustered SE
FE: district_state_id = district_gadm + '_' + state_gadm (631 pairs, not 624)

WHY linearmodels, NOT manual numpy:
  Manual 2SLS (first stage -> fitted values -> second stage OLS) produces
  incorrect SE because second stage OLS residuals use y - X_hat*beta, not
  the structural residuals y - X_actual*beta. linearmodels.IV2SLS implements
  the correct sandwich estimator throughout. See Wooldridge (2010) pp. 106-107.
"""

import pandas as pd
import numpy as np
from linearmodels.iv import IV2SLS
import logging
import os
import warnings
warnings.filterwarnings('ignore')


# === SETUP ===
os.makedirs('05_Outputs/Logs', exist_ok=True)
os.makedirs('05_Outputs/Tables', exist_ok=True)

logging.basicConfig(
    filename='05_Outputs/Logs/28_H2_regression.txt',
    level=logging.INFO,
    format='%(message)s',
    filemode='w'
)
log = logging.getLogger(__name__)


print("=" * 70)
print("PHASE 4: H2 IV 2SLS REGRESSION (Lights -> Deposits)")
print("=" * 70)
log.info("=" * 70)
log.info("H2: IV 2SLS REGRESSION")
log.info("Nighttime Lights -> Deposit Withdrawals")
log.info("Estimator: linearmodels.IV2SLS")
log.info("=" * 70)


# =============================================================================
# STEP 1: LOAD DATA
# =============================================================================
print("\n[1/7] Loading regression-ready panel...")
df = pd.read_csv('03_Data_Clean/regression_panel_final.csv')
assert len(df) == 23347, f"Expected 23,347 rows, got {len(df):,}"
assert df.shape[1] == 23,  f"Expected 23 columns, got {df.shape[1]}"
print(f"  Loaded: {len(df):,} rows, {df.shape[1]} columns -- PASS")
log.info(f"\nPanel loaded: {len(df):,} rows, {df.shape[1]} columns")


# === REQUIRED COLUMNS ===
required_cols = [
    'deposit_change_qt', 'lights_change_qt',
    'flood_exposure_ruleA_qt', 'flood_exposure_ruleB_qt',
    'district_gadm', 'state_gadm', 'quarter'
]
missing_cols = [c for c in required_cols if c not in df.columns]
if missing_cols:
    raise ValueError(f"Missing required columns: {missing_cols}")
print(f"  Required columns verified -- PASS")
log.info(f"Required columns verified: {required_cols}")


# =============================================================================
# STEP 2: RESTRICT TO COMPLETE CASES
# =============================================================================
print("\n[2/7] Restricting to complete cases...")
initial_n = len(df)

df_reg = df[
    df['deposit_change_qt'].notna() &
    df['lights_change_qt'].notna() &
    df['flood_exposure_ruleA_qt'].notna() &
    df['flood_exposure_ruleB_qt'].notna()
].copy()

dropped = initial_n - len(df_reg)
print(f"  Initial:           {initial_n:,} obs")
print(f"  After restriction: {len(df_reg):,} obs  (expected ~22,442)")
print(f"  Dropped:           {dropped:,} obs ({dropped / initial_n * 100:.1f}%)")
log.info(f"\nInitial: {initial_n:,} obs")
log.info(f"After restriction: {len(df_reg):,} obs  (expected ~22,442)")
log.info(f"Dropped: {dropped:,} obs ({dropped / initial_n * 100:.1f}%)")


# =============================================================================
# STEP 3: COMPOSITE KEY + PANEL INDEX
# =============================================================================
print("\n[3/7] Constructing composite key and panel index...")

# CRITICAL: composite key prevents 7 homonymous pairs from collapsing.
# district_gadm alone -> 624 unique districts (WRONG, collapses pairs).
# district_gadm + '_' + state_gadm -> 631 unique district-state pairs (CORRECT).
df_reg['district_state_id'] = df_reg['district_gadm'] + '_' + df_reg['state_gadm']

n_districts = df_reg['district_state_id'].nunique()
n_quarters  = df_reg['quarter'].nunique()

print(f"  Districts (composite): {n_districts}  (expected 631)")
print(f"  Quarters:              {n_quarters}  (expected 36 after log-diff drops 2015Q1)")
log.info(f"\nDistricts (composite): {n_districts}  (expected 631)")
log.info(f"Quarters: {n_quarters}")

if n_districts < 620 or n_districts > 640:
    raise ValueError(
        f"District count {n_districts} outside expected range [620, 640]. "
        f"Check composite key or upstream pipeline."
    )

# linearmodels requires MultiIndex (entity, time)
df_reg = df_reg.set_index(['district_state_id', 'quarter'])
print(f"  Panel index set: (district_state_id, quarter) -- PASS")
log.info("Panel index set: (district_state_id, quarter) -- PASS")


# =============================================================================
# STEP 4: FIXED EFFECTS DUMMIES
# =============================================================================
print("\n[4/7] Constructing fixed effects dummies...")

# Reset index temporarily for get_dummies, then re-align
df_reset = df_reg.reset_index()

district_dummies = pd.get_dummies(
    df_reset['district_state_id'], prefix='d', drop_first=True
).astype(float)
quarter_dummies  = pd.get_dummies(
    df_reset['quarter'], prefix='q', drop_first=True
).astype(float)

n_district_fe = district_dummies.shape[1]
n_quarter_fe  = quarter_dummies.shape[1]

print(f"  District FE dummies: {n_district_fe}  (expected 630 = 631 - 1 reference)")
print(f"  Quarter FE dummies:  {n_quarter_fe}   (expected 35 = 36 - 1 reference)")
log.info(f"\nDistrict FE dummies: {n_district_fe}  (expected 630)")
log.info(f"Quarter FE dummies:  {n_quarter_fe}   (expected 35)")

if n_district_fe < 619 or n_district_fe > 640:
    raise ValueError(
        f"District FE dummy count {n_district_fe} outside expected range. "
        f"Check composite key construction."
    )


# =============================================================================
# STEP 5: ASSEMBLE IV2SLS COMPONENTS
# =============================================================================
print("\n[5/7] Assembling IV2SLS model components...")

# linearmodels.IV2SLS signature:
#   IV2SLS(dependent, exog, endog, instruments)
#
# dependent:   deposit_change_qt                      [n x 1]
# exog:        constant + district FE + quarter FE   [n x (1 + FE dummies)]
# endog:       lights_change_qt                       [n x 1]
# instruments: flood_exposure_ruleA_qt (Rule A)       [n x 1]
#              flood_exposure_ruleB_qt (Rule B)        [n x 1]

dependent = df_reset[['deposit_change_qt']].copy()
dependent.index = df_reg.index

endog = df_reset[['lights_change_qt']].copy()
endog.index = df_reg.index

const = pd.DataFrame(
    np.ones(len(df_reset)), columns=['const'], index=df_reg.index
)
fe_block = pd.concat(
    [district_dummies.set_index(df_reg.index),
     quarter_dummies.set_index(df_reg.index)],
    axis=1
)
exog = pd.concat([const, fe_block], axis=1)

instr_A = df_reset[['flood_exposure_ruleA_qt']].copy()
instr_A.index = df_reg.index

instr_B = df_reset[['flood_exposure_ruleB_qt']].copy()
instr_B.index = df_reg.index

# Cluster variable for SE (must align with regression index)
clusters = pd.Series(
    df_reset['district_state_id'].values,
    index=df_reg.index,
    name='district_state_id'
)

print(f"  Dependent:   {dependent.shape}  -- deposit_change_qt")
print(f"  Exog:        {exog.shape}       -- const + {n_district_fe} district FE + {n_quarter_fe} quarter FE")
print(f"  Endog:       {endog.shape}      -- lights_change_qt")
print(f"  Instrument A:{instr_A.shape}    -- flood_exposure_ruleA_qt")
print(f"  Instrument B:{instr_B.shape}    -- flood_exposure_ruleB_qt")
log.info(f"\nDependent: {dependent.shape}")
log.info(f"Exog: {exog.shape}  (const + {n_district_fe} district FE + {n_quarter_fe} quarter FE)")
log.info(f"Endog: {endog.shape}  (lights_change_qt)")
log.info(f"Instrument A: {instr_A.shape}  (flood_ruleA)")
log.info(f"Instrument B: {instr_B.shape}  (flood_ruleB)")


# =============================================================================
# STEP 6: RUN IV 2SLS -- RULE A (PRIMARY)
# =============================================================================
print("\n[6a/7] IV 2SLS -- Rule A (primary instrument)...")
log.info("\n" + "=" * 70)
log.info("RULE A: PRIMARY SPECIFICATION")
log.info("=" * 70)
log.info("Dependent:   deposit_change_qt")
log.info("Endog:       lights_change_qt")
log.info("Instrument:  flood_exposure_ruleA_qt (district OR state fallback)")
log.info("FE:          district_state_id (631) + quarter (36)")
log.info("SE:          Clustered by district_state_id")
log.info("Note:        Rule A state fallback attenuates first stage toward zero.")
log.info("             Second stage beta may be attenuated accordingly.")

try:
    model_A = IV2SLS(
        dependent   = dependent,
        exog        = exog,
        endog       = endog,
        instruments = instr_A
    )
    res_A = model_A.fit(
        cov_type = 'clustered',
        clusters = clusters
    )
    print(f"  Model fitted -- PASS")
    print(f"  N obs:  {res_A.nobs:,.0f}")
    print(f"  R2:     {res_A.rsquared:.4f}")
except Exception as e:
    log.error(f"Rule A IV2SLS failed: {e}")
    raise

# First stage F-statistic (Kleibergen-Paap equivalent in linearmodels)
try:
    fs_A        = res_A.first_stage
    fs_res_A    = fs_A.individual['lights_change_qt']
    first_F_A   = fs_res_A.f_statistic.stat
    first_p_A   = fs_res_A.f_statistic.pval
    first_coef_A = fs_res_A.params['flood_exposure_ruleA_qt']
    first_se_A   = fs_res_A.std_errors['flood_exposure_ruleA_qt']
    first_t_A    = fs_res_A.tstats['flood_exposure_ruleA_qt']
    first_pv_A   = fs_res_A.pvalues['flood_exposure_ruleA_qt']
except Exception as e:
    log.warning(f"First stage extraction failed: {e}")
    first_F_A = np.nan; first_p_A = np.nan
    first_coef_A = np.nan; first_se_A = np.nan
    first_t_A = np.nan; first_pv_A = np.nan
    
    # NOTE: linearmodels first_stage F-statistic overflows numerically when exog
# contains 666+ dummy columns. For a single excluded instrument, F = t^2 exactly.
# Wooldridge (2010) p.104. Replaces linearmodels f_statistic.stat throughout.
first_F_A = first_t_A ** 2

# Second stage results
coef_A  = res_A.params['lights_change_qt']
se_A    = res_A.std_errors['lights_change_qt']
tstat_A = res_A.tstats['lights_change_qt']
pval_A  = res_A.pvalues['lights_change_qt']
ci_A    = res_A.conf_int().loc['lights_change_qt']
ci_lo_A = ci_A.iloc[0]
ci_hi_A = ci_A.iloc[1]

if pval_A < 0.01:   sig_A = "***"
elif pval_A < 0.05: sig_A = "**"
elif pval_A < 0.10: sig_A = "*"
else:               sig_A = ""

# Instrument credibility gate (pre-committed)
if first_F_A < 10:
    iv_credibility_A = "WEAK INSTRUMENT (F < 10). Label 2SLS as suggestive. Drop causal language."
elif first_F_A < 16.38:
    iv_credibility_A = "MODERATE INSTRUMENT (10 <= F < 16.38). Proceed with caution."
else:
    iv_credibility_A = "STRONG INSTRUMENT (F >= 16.38). IV credible."

print(f"\n  FIRST STAGE (Rule A):")
print(f"    Beta (flood -> lights): {first_coef_A:.6f}")
print(f"    SE:                     {first_se_A:.6f}")
print(f"    t:                      {first_t_A:.3f}")
print(f"    p:                      {first_pv_A:.6f}")
print(f"    F-statistic:            {first_F_A:.3f}")
print(f"    Credibility:            {iv_credibility_A}")
print(f"\n  SECOND STAGE (Rule A):")
print(f"    Beta (lights -> deposits): {coef_A:.6f}")
print(f"    SE:                        {se_A:.6f}")
print(f"    t:                         {tstat_A:.3f}")
print(f"    p:                         {pval_A:.6f}")
print(f"    95% CI:                    [{ci_lo_A:.6f}, {ci_hi_A:.6f}]")
print(f"    N:                         {res_A.nobs:,.0f}")
print(f"    Status:                    {sig_A if sig_A else 'NOT SIGNIFICANT'}")

log.info(f"\nFIRST STAGE:")
log.info(f"  Beta (flood -> lights): {first_coef_A:.6f}")
log.info(f"  SE:     {first_se_A:.6f}")
log.info(f"  t:      {first_t_A:.3f}")
log.info(f"  p:      {first_pv_A:.6f}")
log.info(f"  F-statistic: {first_F_A:.3f}")
log.info(f"  Credibility: {iv_credibility_A}")
log.info(f"\nSECOND STAGE:")
log.info(f"  Beta (lights_hat -> deposits): {coef_A:.6f}")
log.info(f"  SE:      {se_A:.6f}")
log.info(f"  t:       {tstat_A:.3f}")
log.info(f"  p:       {pval_A:.6f}")
log.info(f"  95% CI:  [{ci_lo_A:.6f}, {ci_hi_A:.6f}]")
log.info(f"  N obs:   {res_A.nobs:,.0f}")
log.info(f"  Status:  {sig_A if sig_A else 'NOT SIGNIFICANT'}")

log.info("\nINTERPRETATION (pre-committed, not post-hoc):")
if pval_A < 0.05 and coef_A > 0:
    log.info("  Conclusion: H2 SUPPORTED. Lights declines predict deposit declines.")
    log.info("  Sign positive as expected (both negative in shock -> positive slope).")
elif pval_A >= 0.05:
    log.info("  Conclusion: H2 NULL. No significant lights-to-deposits transmission.")
    log.info("  Pre-committed explanation order: (1) lights are noisy proxy,")
    log.info("  (2) non-migration channels, (3) lagged effects -- see H3.")
else:
    log.info(f"  Conclusion: Coefficient negative ({coef_A:.6f}). Unexpected sign.")
    log.info("  Review specification before interpreting.")


# =============================================================================
# STEP 6b: RUN IV 2SLS -- RULE B (ROBUSTNESS)
# =============================================================================
print("\n[6b/7] IV 2SLS -- Rule B (robustness instrument)...")
log.info("\n" + "=" * 70)
log.info("RULE B: ROBUSTNESS SPECIFICATION")
log.info("=" * 70)
log.info("Instrument:  flood_exposure_ruleB_qt (district-only, high precision)")
log.info("Note:        Rule B -- no state attenuation. Lower power (0.90% rate).")

try:
    model_B = IV2SLS(
        dependent   = dependent,
        exog        = exog,
        endog       = endog,
        instruments = instr_B
    )
    res_B = model_B.fit(
        cov_type = 'clustered',
        clusters = clusters
    )
    print(f"  Model fitted -- PASS")
    print(f"  N obs:  {res_B.nobs:,.0f}")
    print(f"  R2:     {res_B.rsquared:.4f}")
except Exception as e:
    log.error(f"Rule B IV2SLS failed: {e}")
    raise

try:
    fs_B        = res_B.first_stage
    fs_res_B    = fs_B.individual['lights_change_qt']
    first_F_B   = fs_res_B.f_statistic.stat
    first_p_B   = fs_res_B.f_statistic.pval
    first_coef_B = fs_res_B.params['flood_exposure_ruleB_qt']
    first_se_B   = fs_res_B.std_errors['flood_exposure_ruleB_qt']
    first_t_B    = fs_res_B.tstats['flood_exposure_ruleB_qt']
    first_pv_B   = fs_res_B.pvalues['flood_exposure_ruleB_qt']
except Exception as e:
    log.warning(f"Rule B first stage extraction failed: {e}")
    first_F_B = np.nan; first_p_B = np.nan
    first_coef_B = np.nan; first_se_B = np.nan
    first_t_B = np.nan; first_pv_B = np.nan
    first_t_B = np.nan; first_pv_B = np.nan

# NOTE: same overflow fix as Rule A. F = t^2 exact for single excluded instrument.
first_F_B = first_t_B ** 2

coef_B  = res_B.params['lights_change_qt']
se_B    = res_B.std_errors['lights_change_qt']
tstat_B = res_B.tstats['lights_change_qt']
pval_B  = res_B.pvalues['lights_change_qt']
ci_B    = res_B.conf_int().loc['lights_change_qt']
ci_lo_B = ci_B.iloc[0]
ci_hi_B = ci_B.iloc[1]

if pval_B < 0.01:   sig_B = "***"
elif pval_B < 0.05: sig_B = "**"
elif pval_B < 0.10: sig_B = "*"
else:               sig_B = ""

if first_F_B < 10:
    iv_credibility_B = "WEAK INSTRUMENT (F < 10). Label 2SLS as suggestive. Drop causal language."
elif first_F_B < 16.38:
    iv_credibility_B = "MODERATE INSTRUMENT (10 <= F < 16.38). Proceed with caution."
else:
    iv_credibility_B = "STRONG INSTRUMENT (F >= 16.38). IV credible."

print(f"\n  FIRST STAGE (Rule B):")
print(f"    Beta (flood -> lights): {first_coef_B:.6f}")
print(f"    SE:                     {first_se_B:.6f}")
print(f"    t:                      {first_t_B:.3f}")
print(f"    p:                      {first_pv_B:.6f}")
print(f"    F-statistic:            {first_F_B:.3f}")
print(f"    Credibility:            {iv_credibility_B}")
print(f"\n  SECOND STAGE (Rule B):")
print(f"    Beta (lights -> deposits): {coef_B:.6f}")
print(f"    SE:                        {se_B:.6f}")
print(f"    t:                         {tstat_B:.3f}")
print(f"    p:                         {pval_B:.6f}")
print(f"    95% CI:                    [{ci_lo_B:.6f}, {ci_hi_B:.6f}]")
print(f"    N:                         {res_B.nobs:,.0f}")
print(f"    Status:                    {sig_B if sig_B else 'NOT SIGNIFICANT'}")

log.info(f"\nFIRST STAGE:")
log.info(f"  Beta (flood -> lights): {first_coef_B:.6f}")
log.info(f"  SE:     {first_se_B:.6f}")
log.info(f"  t:      {first_t_B:.3f}")
log.info(f"  p:      {first_pv_B:.6f}")
log.info(f"  F-statistic: {first_F_B:.3f}")
log.info(f"  Credibility: {iv_credibility_B}")
log.info(f"\nSECOND STAGE:")
log.info(f"  Beta (lights_hat -> deposits): {coef_B:.6f}")
log.info(f"  SE:      {se_B:.6f}")
log.info(f"  t:       {tstat_B:.3f}")
log.info(f"  p:       {pval_B:.6f}")
log.info(f"  95% CI:  [{ci_lo_B:.6f}, {ci_hi_B:.6f}]")
log.info(f"  N obs:   {res_B.nobs:,.0f}")
log.info(f"  Status:  {sig_B if sig_B else 'NOT SIGNIFICANT'}")


# =============================================================================
# SIDE-BY-SIDE SUMMARY
# =============================================================================
print("\n" + "=" * 70)
print("H2 RESULTS SUMMARY")
print("=" * 70)
print(f"  SECOND STAGE: lights_change_qt_hat -> deposit_change_qt")
print(f"  {'Spec':<10} {'Beta':>12} {'SE':>10} {'t':>8} {'p':>10} {'Sig':>5}")
print(f"  {'-'*58}")
print(f"  {'Rule A':<10} {coef_A:>12.6f} {se_A:>10.6f} "
      f"{tstat_A:>8.3f} {pval_A:>10.6f} {sig_A:>5}")
print(f"  {'Rule B':<10} {coef_B:>12.6f} {se_B:>10.6f} "
      f"{tstat_B:>8.3f} {pval_B:>10.6f} {sig_B:>5}")
print(f"  {'-'*58}")
print(f"  FIRST STAGE F: Rule A = {first_F_A:.3f} | Rule B = {first_F_B:.3f}")
print(f"  N: {res_A.nobs:,.0f} | District FE: {n_districts} | Quarter FE: {n_quarters}")
print(f"  SE: Clustered by district_state_id")

log.info("\n" + "=" * 70)
log.info("SIDE-BY-SIDE SUMMARY")
log.info("=" * 70)
log.info(f"  SECOND STAGE: lights_change_qt_hat -> deposit_change_qt")
log.info(f"  {'Spec':<10} {'Beta':>12} {'SE':>10} {'t':>8} {'p':>10} {'Sig':>5}")
log.info(f"  {'-'*58}")
log.info(f"  {'Rule A':<10} {coef_A:>12.6f} {se_A:>10.6f} "
         f"{tstat_A:>8.3f} {pval_A:>10.6f} {sig_A:>5}")
log.info(f"  {'Rule B':<10} {coef_B:>12.6f} {se_B:>10.6f} "
         f"{tstat_B:>8.3f} {pval_B:>10.6f} {sig_B:>5}")
log.info(f"  First Stage F: Rule A = {first_F_A:.3f} | Rule B = {first_F_B:.3f}")
log.info(f"  N: {res_A.nobs:,.0f} | Districts: {n_districts} | Quarters: {n_quarters}")


# =============================================================================
# STEP 7: SAVE OUTPUTS
# =============================================================================
print("\n[7/7] Saving outputs...")

results_df = pd.DataFrame([
    {
        'hypothesis':           'H2',
        'rule':                 'A',
        'stage':                'second',
        'specification':        'deposit_change_qt ~ lights_change_qt_hat + district_FE + quarter_FE',
        'endog_variable':       'lights_change_qt',
        'instrument':           'flood_exposure_ruleA_qt',
        'coefficient':          round(coef_A,       6),
        'std_error':            round(se_A,         6),
        't_statistic':          round(tstat_A,      3),
        'p_value':              round(pval_A,       6),
        'ci_lower_95':          round(ci_lo_A,      6),
        'ci_upper_95':          round(ci_hi_A,      6),
        'n_obs':                int(res_A.nobs),
        'r_squared':            round(res_A.rsquared, 4),
        'first_stage_beta':     round(first_coef_A, 6),
        'first_stage_se':       round(first_se_A,   6),
        'first_stage_t':        round(first_t_A,    3),
        'first_stage_p':        round(first_pv_A,   6),
        'first_stage_F':        round(first_F_A,    3),
        'iv_credibility':       iv_credibility_A,
        'district_fe_count':    n_districts,
        'quarter_fe_count':     n_quarters,
        'se_type':              'clustered_by_district_state_id',
        'estimator':            'linearmodels.IV2SLS',
        'significance':         sig_A,
        'note':                 'Primary. Rule A state fallback may attenuate first stage.'
    },
    {
        'hypothesis':           'H2',
        'rule':                 'B',
        'stage':                'second',
        'specification':        'deposit_change_qt ~ lights_change_qt_hat + district_FE + quarter_FE',
        'endog_variable':       'lights_change_qt',
        'instrument':           'flood_exposure_ruleB_qt',
        'coefficient':          round(coef_B,       6),
        'std_error':            round(se_B,         6),
        't_statistic':          round(tstat_B,      3),
        'p_value':              round(pval_B,       6),
        'ci_lower_95':          round(ci_lo_B,      6),
        'ci_upper_95':          round(ci_hi_B,      6),
        'n_obs':                int(res_B.nobs),
        'r_squared':            round(res_B.rsquared, 4),
        'first_stage_beta':     round(first_coef_B, 6),
        'first_stage_se':       round(first_se_B,   6),
        'first_stage_t':        round(first_t_B,    3),
        'first_stage_p':        round(first_pv_B,   6),
        'first_stage_F':        round(first_F_B,    3),
        'iv_credibility':       iv_credibility_B,
        'district_fe_count':    n_districts,
        'quarter_fe_count':     n_quarters,
        'se_type':              'clustered_by_district_state_id',
        'estimator':            'linearmodels.IV2SLS',
        'significance':         sig_B,
        'note':                 'Robustness. District-only. No state attenuation. Lower power.'
    }
])

results_df.to_csv('05_Outputs/Tables/03_H2_iv2sls.csv', index=False)
print(f"  Table saved: 05_Outputs/Tables/03_H2_iv2sls.csv")
log.info(f"\nTable saved: 05_Outputs/Tables/03_H2_iv2sls.csv")

with open('05_Outputs/Logs/28_H2_regression_full_ruleA.txt', 'w') as f:
    f.write(str(res_A.summary))
print(f"  Full summary (Rule A): 05_Outputs/Logs/28_H2_regression_full_ruleA.txt")
log.info(f"Full summary (Rule A) saved.")

with open('05_Outputs/Logs/28_H2_regression_full_ruleB.txt', 'w') as f:
    f.write(str(res_B.summary))
print(f"  Full summary (Rule B): 05_Outputs/Logs/28_H2_regression_full_ruleB.txt")
log.info(f"Full summary (Rule B) saved.")


# === COMPLETION ===
print("\n" + "=" * 70)
print("H2 IV 2SLS COMPLETE")
print("=" * 70)
print(f"  Table:         05_Outputs/Tables/03_H2_iv2sls.csv")
print(f"  Log:           05_Outputs/Logs/28_H2_regression.txt")
print(f"  Full (Rule A): 05_Outputs/Logs/28_H2_regression_full_ruleA.txt")
print(f"  Full (Rule B): 05_Outputs/Logs/28_H2_regression_full_ruleB.txt")
print("=" * 70)
print("NEXT STEP: Run Script 29 (H3: Distributed Lag -- Flood Timing)")
print("=" * 70)

log.info("\n" + "=" * 70)
log.info("SCRIPT 28 COMPLETE")
log.info("Next: Script 29 -- H3 Distributed Lag (Flood Timing)")
log.info("=" * 70)