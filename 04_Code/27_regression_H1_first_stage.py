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
print("PHASE 4: H1 FIRST STAGE REGRESSION (Floods → Lights)")
print("=" * 70)
log.info("=" * 70)
log.info("H1: FIRST STAGE REGRESSION")
log.info("Floods → Nighttime Lights Decline")
log.info("=" * 70)


# === LOAD DATA ===
print("\n[1/5] Loading regression-ready panel...")
df = pd.read_csv('03_Data_Clean/regression_panel_final.csv')
print(f"  ✓ Loaded: {len(df):,} rows, {df.shape[1]} columns")
log.info(f"\nPanel loaded: {len(df):,} rows, {df.shape[1]} columns")


# === SANITY CHECK: REQUIRED COLUMNS ===
required_cols = ['lights_change_qt', 'flood_exposure_ruleA_qt', 'district_gadm', 'state_gadm', 'quarter']
missing_cols = [c for c in required_cols if c not in df.columns]
if missing_cols:
    raise ValueError(f"Missing required columns: {missing_cols}")
print(f"  ✓ Required columns present: {required_cols}")
log.info(f"Required columns verified: {required_cols}")


# === RESTRICT TO NON-MISSING ===
print("\n[2/5] Restricting to observations with complete data...")
initial_n = len(df)

df_reg = df[
    df['lights_change_qt'].notna() &
    df['flood_exposure_ruleA_qt'].notna()
].copy()

dropped = initial_n - len(df_reg)
print(f"  Initial:           {initial_n:,} obs")
print(f"  After restriction: {len(df_reg):,} obs")
print(f"  Dropped:           {dropped:,} obs ({dropped / initial_n * 100:.1f}%)")
log.info(f"\nInitial: {initial_n:,} obs")
log.info(f"After restriction: {len(df_reg):,} obs")
log.info(f"Dropped: {dropped:,} obs ({dropped / initial_n * 100:.1f}%)")


# === ENCODE FIXED EFFECTS ===
print("\n[3/5] Encoding fixed effects...")

# CRITICAL FIX: Composite district_state_id prevents homonymous district collapse.
# 7 homonymous pairs exist: Aurangabad, Balrampur, Bijapur, Bilaspur,
# Hamirpur, Pratapgarh, Raigarh.
# Without state: 624 district FE categories (wrong — collapses pairs).
# With state composite: 631 district FE categories (correct).
df_reg['district_state_id'] = df_reg['district_gadm'] + '_' + df_reg['state_gadm']
df_reg['district_fe'] = pd.Categorical(df_reg['district_state_id'])
df_reg['quarter_fe'] = pd.Categorical(df_reg['quarter'])

n_district_fe = df_reg['district_fe'].nunique()
n_quarter_fe = df_reg['quarter_fe'].nunique()

print(f"  ✓ District FE: {n_district_fe} categories (expect 631)")
print(f"  ✓ Quarter FE:  {n_quarter_fe} categories (expect 37)")
log.info(f"\nDistrict FE: {n_district_fe} categories (expect 631)")
log.info(f"Quarter FE: {n_quarter_fe} categories (expect 37)")

# Hard stop if FE counts deviate — protects against upstream pipeline errors
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
print(f"  ✓ FE count validation passed")
log.info("FE count validation passed")


# === REGRESSION ===
print("\n[4/5] Running OLS with district + quarter FE, clustered SE...")
log.info("\n" + "=" * 70)
log.info("REGRESSION SPECIFICATION")
log.info("=" * 70)
log.info("Dependent variable:    lights_change_qt  (Δ log nighttime lights, quarterly)")
log.info("Treatment variable:    flood_exposure_ruleA_qt  (binary, Rule A)")
log.info("Fixed effects:         district_state_id (631) + quarter (37)")
log.info("Standard errors:       Clustered by district_state_id")
log.info("Identification:        Within-district variation in flood timing")
log.info("Estimator:             OLS with absorbed FE via C() categoricals")

formula = 'lights_change_qt ~ flood_exposure_ruleA_qt + C(district_fe) + C(quarter_fe)'

try:
    model = ols(formula, data=df_reg).fit(
        cov_type='cluster',
        cov_kwds={'groups': df_reg['district_state_id']}
    )
    print(f"  ✓ Model fitted")
    print(f"  ✓ N obs:  {model.nobs:,.0f}")
    print(f"  ✓ R²:     {model.rsquared:.4f}")
    print(f"  ✓ R²-adj: {model.rsquared_adj:.4f}")
    log.info(f"\nModel fitted successfully")
    log.info(f"N obs:        {model.nobs:,.0f}")
    log.info(f"R²:           {model.rsquared:.4f}")
    log.info(f"R²-adjusted:  {model.rsquared_adj:.4f}")
except Exception as e:
    log.error(f"Model fitting failed: {e}")
    raise


# === EXTRACT KEY RESULTS ===
print("\n[5/5] Extracting results...")

flood_coef  = model.params.get('flood_exposure_ruleA_qt', np.nan)
flood_se    = model.bse.get('flood_exposure_ruleA_qt', np.nan)
flood_tstat = model.tvalues.get('flood_exposure_ruleA_qt', np.nan)
flood_pval  = model.pvalues.get('flood_exposure_ruleA_qt', np.nan)
flood_ci_lo = model.conf_int().loc['flood_exposure_ruleA_qt', 0] if 'flood_exposure_ruleA_qt' in model.conf_int().index else np.nan
flood_ci_hi = model.conf_int().loc['flood_exposure_ruleA_qt', 1] if 'flood_exposure_ruleA_qt' in model.conf_int().index else np.nan

if flood_pval < 0.01:
    sig_label = "***"
    sig_text  = "HIGHLY SIGNIFICANT (p < 0.01)"
elif flood_pval < 0.05:
    sig_label = "**"
    sig_text  = "SIGNIFICANT (p < 0.05)"
elif flood_pval < 0.10:
    sig_label = "*"
    sig_text  = "WEAKLY SIGNIFICANT (p < 0.10)"
else:
    sig_label = ""
    sig_text  = "NOT SIGNIFICANT (p ≥ 0.10)"

print(f"\n  RESULT: flood_exposure_ruleA_qt → lights_change_qt")
print(f"    β̂        = {flood_coef:.6f}")
print(f"    SE       = {flood_se:.6f}")
print(f"    t        = {flood_tstat:.3f}")
print(f"    p        = {flood_pval:.6f}")
print(f"    95% CI   = [{flood_ci_lo:.6f}, {flood_ci_hi:.6f}]")
print(f"    N        = {model.nobs:,.0f}")
print(f"    Status:  {sig_text} {sig_label}")

log.info("\n" + "=" * 70)
log.info("RESULTS: flood_exposure_ruleA_qt → lights_change_qt")
log.info("=" * 70)
log.info(f"Coefficient:   {flood_coef:.6f}")
log.info(f"Std Error:     {flood_se:.6f}")
log.info(f"t-statistic:   {flood_tstat:.3f}")
log.info(f"p-value:       {flood_pval:.6f}")
log.info(f"95% CI:        [{flood_ci_lo:.6f}, {flood_ci_hi:.6f}]")
log.info(f"N obs:         {model.nobs:,.0f}")
log.info(f"Significance:  {sig_text} {sig_label}")

log.info("\n" + "-" * 70)
log.info("INTERPRETATION (pre-committed, not post-hoc):")
log.info("  H1 tests whether flood exposure reduces nighttime light intensity.")
log.info("  A negative, significant coefficient supports the displacement/disruption")
log.info("  channel and validates flood exposure as a credible instrument for H2.")
log.info(f"  Expected sign: negative (β < 0).")
log.info(f"  Observed sign: {'negative' if flood_coef < 0 else 'positive'} (β = {flood_coef:.6f}).")
if flood_pval < 0.05:
    log.info("  Conclusion: H1 SUPPORTED. Floods reduce nighttime lights.")
    log.info("  Instrument credibility: CONFIRMED for H2 IV 2SLS.")
else:
    log.info("  Conclusion: H1 NOT SUPPORTED at 5% level.")
    log.info("  Instrument credibility: WEAK — proceed to H2 with caution.")


# === SAVE OUTPUTS ===
results_df = pd.DataFrame([{
    'hypothesis':           'H1',
    'specification':        'lights_change_qt ~ flood_ruleA + district_FE + quarter_FE',
    'variable':             'flood_exposure_ruleA_qt',
    'coefficient':          round(flood_coef, 6),
    'std_error':            round(flood_se, 6),
    't_statistic':          round(flood_tstat, 3),
    'p_value':              round(flood_pval, 6),
    'ci_lower_95':          round(flood_ci_lo, 6),
    'ci_upper_95':          round(flood_ci_hi, 6),
    'n_obs':                int(model.nobs),
    'r_squared':            round(model.rsquared, 4),
    'r_squared_adj':        round(model.rsquared_adj, 4),
    'district_fe_count':    n_district_fe,
    'quarter_fe_count':     n_quarter_fe,
    'se_type':              'clustered_by_district_state_id',
    'significance':         sig_label
}])

results_df.to_csv('05_Outputs/Tables/02_H1_first_stage.csv', index=False)
print(f"\n  ✓ Table saved: 05_Outputs/Tables/02_H1_first_stage.csv")
log.info(f"\nTable saved: 05_Outputs/Tables/02_H1_first_stage.csv")

with open('05_Outputs/Logs/27_H1_regression_full.txt', 'w') as f:
    f.write(str(model.summary()))
print(f"  ✓ Full summary saved: 05_Outputs/Logs/27_H1_regression_full.txt")
log.info(f"Full summary saved: 05_Outputs/Logs/27_H1_regression_full.txt")


# === COMPLETION ===
print("\n" + "=" * 70)
print("H1 FIRST STAGE COMPLETE")
print("=" * 70)
print(f"  Table:    05_Outputs/Tables/02_H1_first_stage.csv")
print(f"  Log:      05_Outputs/Logs/27_H1_regression.txt")
print(f"  Full log: 05_Outputs/Logs/27_H1_regression_full.txt")
print("=" * 70)
print("\nNEXT STEP: Run Script 28 (H2: IV 2SLS — Lights → Deposits)")
print("=" * 70)

log.info("\n" + "=" * 70)
log.info("SCRIPT 27 COMPLETE")
log.info("Next: Script 28 — H2 IV 2SLS (Lights → Deposits)")
log.info("=" * 70)