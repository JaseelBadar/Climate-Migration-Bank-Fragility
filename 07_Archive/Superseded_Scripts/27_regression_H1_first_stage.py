"""
27_regression_H1_first_stage.py
H1: Floods -> Nighttime Lights Decline
OLS with district (composite) + quarter FE, clustered SE.
Both Rule A (primary) and Rule B (robustness) estimated.
FE CORRECTION: district_state_id = district_gadm + '_' + state_gadm
               631 FE categories (not 624 -- homonymous pair fix)
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
    filename='05_Outputs/Logs/27_H1_regression.txt',
    level=logging.INFO,
    format='%(message)s',
    filemode='w'
)
log = logging.getLogger(__name__)


print("=" * 70)
print("PHASE 4: H1 FIRST STAGE REGRESSION (Floods -> Lights)")
print("=" * 70)
log.info("=" * 70)
log.info("H1: FIRST STAGE REGRESSION")
log.info("Floods -> Nighttime Lights Decline")
log.info("=" * 70)


# === LOAD DATA ===
print("\n[1/6] Loading regression-ready panel...")
df = pd.read_csv('03_Data_Clean/regression_panel_final.csv')
assert len(df) == 23347, f"Expected 23,347 rows, got {len(df):,}"
assert df.shape[1] == 23,  f"Expected 23 columns, got {df.shape[1]}"
print(f"  Loaded: {len(df):,} rows, {df.shape[1]} columns -- PASS")
log.info(f"\nPanel loaded: {len(df):,} rows, {df.shape[1]} columns")


# === SANITY CHECK: REQUIRED COLUMNS ===
required_cols = [
    'lights_change_qt', 'deposit_change_qt',
    'flood_exposure_ruleA_qt', 'flood_exposure_ruleB_qt',
    'district_gadm', 'state_gadm', 'quarter'
]
missing_cols = [c for c in required_cols if c not in df.columns]
if missing_cols:
    raise ValueError(f"Missing required columns: {missing_cols}")
print(f"  Required columns verified -- PASS")
log.info(f"Required columns verified: {required_cols}")


# === RESTRICT TO NON-MISSING (shared sample for both rules) ===
print("\n[2/6] Restricting to observations with complete data...")
initial_n = len(df)

df_reg = df[
    df['lights_change_qt'].notna() &
    df['flood_exposure_ruleA_qt'].notna() &
    df['flood_exposure_ruleB_qt'].notna()
].copy()

dropped = initial_n - len(df_reg)
print(f"  Initial:           {initial_n:,} obs")
print(f"  After restriction: {len(df_reg):,} obs  (expected 22,716)")
print(f"  Dropped:           {dropped:,} obs ({dropped / initial_n * 100:.1f}%)")
log.info(f"\nInitial: {initial_n:,} obs")
log.info(f"After restriction: {len(df_reg):,} obs  (expected 22,716)")
log.info(f"Dropped: {dropped:,} obs ({dropped / initial_n * 100:.1f}%)")


# === ENCODE FIXED EFFECTS ===
print("\n[3/6] Encoding fixed effects...")

# COMPOSITE KEY: prevents 7 homonymous district pairs from collapsing.
# district_gadm alone -> 624 FE (WRONG).
# district_gadm + '_' + state_gadm -> 631 FE (CORRECT).
df_reg['district_state_id'] = df_reg['district_gadm'] + '_' + df_reg['state_gadm']
df_reg['district_fe']       = pd.Categorical(df_reg['district_state_id'])
df_reg['quarter_fe']        = pd.Categorical(df_reg['quarter'])

n_district_fe = df_reg['district_fe'].nunique()
n_quarter_fe  = df_reg['quarter_fe'].nunique()

print(f"  District FE: {n_district_fe} categories (expected 631)")
print(f"  Quarter FE:  {n_quarter_fe} categories (expected 37)")
log.info(f"\nDistrict FE: {n_district_fe} categories (expected 631)")
log.info(f"Quarter FE:  {n_quarter_fe} categories (expected 37)")

if n_district_fe < 620 or n_district_fe > 640:
    raise ValueError(
        f"District FE count {n_district_fe} outside expected range [620, 640]. "
        f"Check composite key construction or upstream pipeline."
    )
if n_quarter_fe < 35 or n_quarter_fe > 40:
    raise ValueError(
        f"Quarter FE count {n_quarter_fe} outside expected range [35, 40]. "
        f"Check panel time coverage."
    )
print(f"  FE count validation -- PASS")
log.info("FE count validation -- PASS")


# =============================================================================
# RULE A: Primary specification
# =============================================================================
print("\n[4/6] Rule A: OLS with district + quarter FE, clustered SE...")
log.info("\n" + "=" * 70)
log.info("RULE A: PRIMARY SPECIFICATION")
log.info("=" * 70)
log.info("Dependent variable:  lights_change_qt  (Delta log nighttime lights)")
log.info("Treatment variable:  flood_exposure_ruleA_qt  (binary, district OR state)")
log.info("Fixed effects:       district_state_id (631) + quarter (37)")
log.info("Standard errors:     Clustered by district_state_id")
log.info("Note:                Rule A uses state fallback. Beta attenuated toward")
log.info("                     zero. Estimate is conservative lower bound.")

formula_A = 'lights_change_qt ~ flood_exposure_ruleA_qt + C(district_fe) + C(quarter_fe)'

try:
    model_A = ols(formula_A, data=df_reg).fit(
        cov_type='cluster',
        cov_kwds={'groups': df_reg['district_state_id']}
    )
    print(f"  Model fitted -- PASS")
    print(f"  N obs:  {model_A.nobs:,.0f}")
    print(f"  R2:     {model_A.rsquared:.4f}")
    print(f"  R2-adj: {model_A.rsquared_adj:.4f}")
    log.info(f"\nModel fitted successfully")
    log.info(f"N obs:       {model_A.nobs:,.0f}")
    log.info(f"R2:          {model_A.rsquared:.4f}")
    log.info(f"R2-adjusted: {model_A.rsquared_adj:.4f}")
except Exception as e:
    log.error(f"Rule A model fitting failed: {e}")
    raise

flood_coef_A  = model_A.params.get('flood_exposure_ruleA_qt', np.nan)
flood_se_A    = model_A.bse.get('flood_exposure_ruleA_qt', np.nan)
flood_tstat_A = model_A.tvalues.get('flood_exposure_ruleA_qt', np.nan)
flood_pval_A  = model_A.pvalues.get('flood_exposure_ruleA_qt', np.nan)
flood_ci_A    = model_A.conf_int()
flood_ci_lo_A = flood_ci_A.loc['flood_exposure_ruleA_qt', 0]
flood_ci_hi_A = flood_ci_A.loc['flood_exposure_ruleA_qt', 1]

if flood_pval_A < 0.01:   sig_A = "***"
elif flood_pval_A < 0.05: sig_A = "**"
elif flood_pval_A < 0.10: sig_A = "*"
else:                      sig_A = ""

if flood_pval_A < 0.05:
    sig_text_A = "SIGNIFICANT (p < 0.05)"
elif flood_pval_A < 0.10:
    sig_text_A = "WEAKLY SIGNIFICANT (p < 0.10)"
else:
    sig_text_A = "NOT SIGNIFICANT (p >= 0.10)"

print(f"\n  RULE A RESULT: flood_exposure_ruleA_qt -> lights_change_qt")
print(f"    Beta    = {flood_coef_A:.6f}")
print(f"    SE      = {flood_se_A:.6f}")
print(f"    t       = {flood_tstat_A:.3f}")
print(f"    p       = {flood_pval_A:.6f}")
print(f"    95% CI  = [{flood_ci_lo_A:.6f}, {flood_ci_hi_A:.6f}]")
print(f"    N       = {model_A.nobs:,.0f}")
print(f"    Status: {sig_text_A} {sig_A}")

log.info(f"\nCoefficient:   {flood_coef_A:.6f}")
log.info(f"Std Error:     {flood_se_A:.6f}")
log.info(f"t-statistic:   {flood_tstat_A:.3f}")
log.info(f"p-value:       {flood_pval_A:.6f}")
log.info(f"95% CI:        [{flood_ci_lo_A:.6f}, {flood_ci_hi_A:.6f}]")
log.info(f"N obs:         {model_A.nobs:,.0f}")
log.info(f"Significance:  {sig_text_A} {sig_A}")
log.info(f"Observed sign: {'negative' if flood_coef_A < 0 else 'positive'} (expected: negative)")

log.info("\nINTERPRETATION (pre-committed, not post-hoc):")
log.info("  H1 tests whether flood exposure reduces nighttime light intensity.")
log.info("  A negative, significant coefficient supports the displacement/disruption")
log.info("  channel and validates flood exposure as a credible instrument for H2.")
if flood_pval_A < 0.05 and flood_coef_A < 0:
    log.info("  Conclusion: H1 SUPPORTED. Floods reduce nighttime lights.")
    log.info("  Instrument credibility: CONFIRMED for H2 IV 2SLS.")
elif flood_pval_A < 0.05 and flood_coef_A > 0:
    log.info("  Conclusion: H1 REJECTED. Coefficient positive -- lights increase.")
    log.info("  Instrument credibility: INVALID. Review specification.")
else:
    log.info("  Conclusion: H1 NOT SUPPORTED at 5% level.")
    log.info("  Instrument credibility: WEAK -- proceed to H2 with caution.")


# =============================================================================
# RULE B: Robustness / high-precision specification
# =============================================================================
print("\n[5/6] Rule B: OLS with district + quarter FE, clustered SE...")
log.info("\n" + "=" * 70)
log.info("RULE B: ROBUSTNESS SPECIFICATION")
log.info("=" * 70)
log.info("Dependent variable:  lights_change_qt  (Delta log nighttime lights)")
log.info("Treatment variable:  flood_exposure_ruleB_qt  (binary, district-only)")
log.info("Fixed effects:       district_state_id (631) + quarter (37)")
log.info("Standard errors:     Clustered by district_state_id")
log.info("Note:                Rule B = district-only match. No state attenuation.")
log.info("                     Higher precision. Lower power (0.90% treatment rate).")
log.info("                     Compare with Rule A for attenuation bound.")

formula_B = 'lights_change_qt ~ flood_exposure_ruleB_qt + C(district_fe) + C(quarter_fe)'

try:
    model_B = ols(formula_B, data=df_reg).fit(
        cov_type='cluster',
        cov_kwds={'groups': df_reg['district_state_id']}
    )
    print(f"  Model fitted -- PASS")
    print(f"  N obs:  {model_B.nobs:,.0f}")
    print(f"  R2:     {model_B.rsquared:.4f}")
    print(f"  R2-adj: {model_B.rsquared_adj:.4f}")
    log.info(f"\nModel fitted successfully")
    log.info(f"N obs:       {model_B.nobs:,.0f}")
    log.info(f"R2:          {model_B.rsquared:.4f}")
    log.info(f"R2-adjusted: {model_B.rsquared_adj:.4f}")
except Exception as e:
    log.error(f"Rule B model fitting failed: {e}")
    raise

flood_coef_B  = model_B.params.get('flood_exposure_ruleB_qt', np.nan)
flood_se_B    = model_B.bse.get('flood_exposure_ruleB_qt', np.nan)
flood_tstat_B = model_B.tvalues.get('flood_exposure_ruleB_qt', np.nan)
flood_pval_B  = model_B.pvalues.get('flood_exposure_ruleB_qt', np.nan)
flood_ci_B    = model_B.conf_int()
flood_ci_lo_B = flood_ci_B.loc['flood_exposure_ruleB_qt', 0]
flood_ci_hi_B = flood_ci_B.loc['flood_exposure_ruleB_qt', 1]

if flood_pval_B < 0.01:   sig_B = "***"
elif flood_pval_B < 0.05: sig_B = "**"
elif flood_pval_B < 0.10: sig_B = "*"
else:                      sig_B = ""

if flood_pval_B < 0.05:
    sig_text_B = "SIGNIFICANT (p < 0.05)"
elif flood_pval_B < 0.10:
    sig_text_B = "WEAKLY SIGNIFICANT (p < 0.10)"
else:
    sig_text_B = "NOT SIGNIFICANT (p >= 0.10)"

print(f"\n  RULE B RESULT: flood_exposure_ruleB_qt -> lights_change_qt")
print(f"    Beta    = {flood_coef_B:.6f}")
print(f"    SE      = {flood_se_B:.6f}")
print(f"    t       = {flood_tstat_B:.3f}")
print(f"    p       = {flood_pval_B:.6f}")
print(f"    95% CI  = [{flood_ci_lo_B:.6f}, {flood_ci_hi_B:.6f}]")
print(f"    N       = {model_B.nobs:,.0f}")
print(f"    Status: {sig_text_B} {sig_B}")

log.info(f"\nCoefficient:   {flood_coef_B:.6f}")
log.info(f"Std Error:     {flood_se_B:.6f}")
log.info(f"t-statistic:   {flood_tstat_B:.3f}")
log.info(f"p-value:       {flood_pval_B:.6f}")
log.info(f"95% CI:        [{flood_ci_lo_B:.6f}, {flood_ci_hi_B:.6f}]")
log.info(f"N obs:         {model_B.nobs:,.0f}")
log.info(f"Significance:  {sig_text_B} {sig_B}")
log.info(f"Observed sign: {'negative' if flood_coef_B < 0 else 'positive'} (expected: negative)")


# =============================================================================
# SIDE-BY-SIDE SUMMARY
# =============================================================================
print("\n" + "=" * 70)
print("H1 RESULTS SUMMARY")
print("=" * 70)
print(f"  {'Spec':<10} {'Beta':>12} {'SE':>10} {'t':>8} {'p':>10} {'Sig':>5}")
print(f"  {'-'*58}")
print(f"  {'Rule A':<10} {flood_coef_A:>12.6f} {flood_se_A:>10.6f} "
      f"{flood_tstat_A:>8.3f} {flood_pval_A:>10.6f} {sig_A:>5}")
print(f"  {'Rule B':<10} {flood_coef_B:>12.6f} {flood_se_B:>10.6f} "
      f"{flood_tstat_B:>8.3f} {flood_pval_B:>10.6f} {sig_B:>5}")
print(f"  {'-'*58}")
print(f"  N (both): {model_A.nobs:,.0f}")
print(f"  District FE: {n_district_fe} | Quarter FE: {n_quarter_fe}")
print(f"  SE: Clustered by district_state_id")

log.info("\n" + "=" * 70)
log.info("SIDE-BY-SIDE SUMMARY")
log.info("=" * 70)
log.info(f"  {'Spec':<10} {'Beta':>12} {'SE':>10} {'t':>8} {'p':>10} {'Sig':>5}")
log.info(f"  {'-'*58}")
log.info(f"  {'Rule A':<10} {flood_coef_A:>12.6f} {flood_se_A:>10.6f} "
         f"{flood_tstat_A:>8.3f} {flood_pval_A:>10.6f} {sig_A:>5}")
log.info(f"  {'Rule B':<10} {flood_coef_B:>12.6f} {flood_se_B:>10.6f} "
         f"{flood_tstat_B:>8.3f} {flood_pval_B:>10.6f} {sig_B:>5}")
log.info(f"  N: {model_A.nobs:,.0f} | District FE: {n_district_fe} | Quarter FE: {n_quarter_fe}")
log.info(f"  SE: Clustered by district_state_id")


# =============================================================================
# SAVE OUTPUTS
# =============================================================================
print("\n[6/6] Saving outputs...")

results_df = pd.DataFrame([
    {
        'hypothesis':        'H1',
        'rule':              'A',
        'specification':     'lights_change_qt ~ flood_ruleA + district_FE + quarter_FE',
        'variable':          'flood_exposure_ruleA_qt',
        'coefficient':       round(flood_coef_A,    6),
        'std_error':         round(flood_se_A,      6),
        't_statistic':       round(flood_tstat_A,   3),
        'p_value':           round(flood_pval_A,    6),
        'ci_lower_95':       round(flood_ci_lo_A,   6),
        'ci_upper_95':       round(flood_ci_hi_A,   6),
        'n_obs':             int(model_A.nobs),
        'r_squared':         round(model_A.rsquared,     4),
        'r_squared_adj':     round(model_A.rsquared_adj, 4),
        'district_fe_count': n_district_fe,
        'quarter_fe_count':  n_quarter_fe,
        'se_type':           'clustered_by_district_state_id',
        'significance':      sig_A,
        'note':              'Primary. State fallback attenuates beta toward zero. Conservative lower bound.'
    },
    {
        'hypothesis':        'H1',
        'rule':              'B',
        'specification':     'lights_change_qt ~ flood_ruleB + district_FE + quarter_FE',
        'variable':          'flood_exposure_ruleB_qt',
        'coefficient':       round(flood_coef_B,    6),
        'std_error':         round(flood_se_B,      6),
        't_statistic':       round(flood_tstat_B,   3),
        'p_value':           round(flood_pval_B,    6),
        'ci_lower_95':       round(flood_ci_lo_B,   6),
        'ci_upper_95':       round(flood_ci_hi_B,   6),
        'n_obs':             int(model_B.nobs),
        'r_squared':         round(model_B.rsquared,     4),
        'r_squared_adj':     round(model_B.rsquared_adj, 4),
        'district_fe_count': n_district_fe,
        'quarter_fe_count':  n_quarter_fe,
        'se_type':           'clustered_by_district_state_id',
        'significance':      sig_B,
        'note':              'Robustness. District-only match. No state attenuation. Lower power.'
    }
])

results_df.to_csv('05_Outputs/Tables/02_H1_first_stage.csv', index=False)
print(f"  Table saved: 05_Outputs/Tables/02_H1_first_stage.csv")
log.info(f"\nTable saved: 05_Outputs/Tables/02_H1_first_stage.csv")

with open('05_Outputs/Logs/27_H1_regression_full_ruleA.txt', 'w') as f:
    f.write(str(model_A.summary()))
print(f"  Full summary (Rule A): 05_Outputs/Logs/27_H1_regression_full_ruleA.txt")
log.info(f"Full summary (Rule A) saved.")

with open('05_Outputs/Logs/27_H1_regression_full_ruleB.txt', 'w') as f:
    f.write(str(model_B.summary()))
print(f"  Full summary (Rule B): 05_Outputs/Logs/27_H1_regression_full_ruleB.txt")
log.info(f"Full summary (Rule B) saved.")


# === COMPLETION ===
print("\n" + "=" * 70)
print("H1 FIRST STAGE COMPLETE")
print("=" * 70)
print(f"  Table:         05_Outputs/Tables/02_H1_first_stage.csv")
print(f"  Log:           05_Outputs/Logs/27_H1_regression.txt")
print(f"  Full (Rule A): 05_Outputs/Logs/27_H1_regression_full_ruleA.txt")
print(f"  Full (Rule B): 05_Outputs/Logs/27_H1_regression_full_ruleB.txt")
print("=" * 70)
print("NEXT STEP: Run Script 28 (H2: IV 2SLS -- Lights -> Deposits)")
print("=" * 70)

log.info("\n" + "=" * 70)
log.info("SCRIPT 27 COMPLETE")
log.info("Next: Script 28 -- H2 IV 2SLS (Lights -> Deposits)")
log.info("=" * 70)